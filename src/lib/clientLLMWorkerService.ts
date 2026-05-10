import { LLM_CONFIG } from './llmConfig';
import { openRouterLLMService } from './openRouterLLM';

type LocalInferenceState =
  | 'unknown'
  | 'worker_unavailable'
  | 'cold'
  | 'loading'
  | 'loaded_unprobed'
  | 'probing'
  | 'ready'
  | 'unhealthy';

interface PendingWorkerRequest {
  type: string;
  startedAt: number;
  timeoutMs: number;
  resolve: (value: any) => void;
  reject: (reason?: any) => void;
}

interface LocalInferenceHealth {
  state: LocalInferenceState;
  proven: boolean;
  lastProbeAt?: string;
  lastSuccessAt?: string;
  lastFailureAt?: string;
  lastFailureReason?: string;
  lastGenerationDurationMs?: number;
  lastProbeDurationMs?: number;
  consecutiveFailures: number;
}

// Service to manage client-side LLM processing using Web Workers with WebGPU model support
class ClientLLMWorkerService {
  private worker: Worker | null = null;
  private isInitialized = false;
  private isInitializing = false;
  private requestCounter = 0;
  private pendingRequests = new Map<string, PendingWorkerRequest>();
  private currentModel = LLM_CONFIG.CLIENT_MODEL;
  private capabilities = { webGPU: false, simd: false };
  private backgroundWarmupPromise: Promise<void> | null = null;
  private localProbePromise: Promise<boolean> | null = null;
  private localGenerationUnhealthy = false;
  private localHealth: LocalInferenceHealth = {
    state: 'unknown',
    proven: false,
    consecutiveFailures: 0,
  };
  private localRetryAfter = 0;

  constructor() {
    this.initializeWorker();
    this.installDebugHooks();
  }

  private initializeWorker(): void {
    try {
      // Create worker from the worker file
      this.worker = new Worker(
        new URL('../workers/clientLLMWorker.ts', import.meta.url),
        { type: 'module' }
      );

      this.worker.onmessage = this.handleWorkerMessage.bind(this);
      this.worker.onerror = this.handleWorkerError.bind(this);
      if (this.localHealth.state !== 'unhealthy') {
        this.localHealth.state = 'cold';
      }
      
      console.log('Enhanced Client LLM Worker created with WebGPU model support');
    } catch (error) {
      console.error('Failed to create Client LLM Worker:', error);
      this.localHealth.state = 'worker_unavailable';
      this.localHealth.lastFailureAt = new Date().toISOString();
      this.localHealth.lastFailureReason = error instanceof Error ? error.message : String(error);
    }
  }

  private installDebugHooks(): void {
    if (typeof window === 'undefined') {
      return;
    }

    (window as any).__PORTLAND_LLM__ = {
      getStatus: () => this.getStatus(),
      getCloudFallbackStatus: () => this.getCloudFallbackStatus(),
      probeLocalInference: () => this.probeLocalInference({ force: true }),
      warmLocalModel: () => this.warmLocalModelInBackground({ force: true }),
      resetLocalWorker: () => this.resetLocalWorker('manual debug reset'),
    };
  }

  private emitServiceDiagnostic(event: string, data: Record<string, unknown> = {}): void {
    const detail = {
      event,
      timestamp: new Date().toISOString(),
      modelName: this.currentModel,
      localHealth: { ...this.localHealth },
      cloudFallback: openRouterLLMService.getConfigurationStatus(),
      ...data,
    };
    console.log(`[ClientLLMWorkerService] ${event}`, detail);
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('clientLLMServiceDiagnostic', { detail }));
    }
  }

  private handleWorkerMessage(event: MessageEvent): void {
    const { id, success, data, error } = event.data;
    if (data?.diagnostic || data?.progress) {
      const eventName = data.diagnostic ? 'clientLLMDiagnostic' : 'clientLLMProgress';
      console.debug(`[ClientLLMWorkerService] ${eventName}`, data.diagnostic || data.progress);
      window.dispatchEvent(new CustomEvent(eventName, { detail: data.diagnostic || data.progress }));
      return;
    }

    const pendingRequest = this.pendingRequests.get(id);
    
    if (pendingRequest) {
      this.pendingRequests.delete(id);
      
      if (success) {
        // Update local state based on response
        if (data.capabilities) {
          this.capabilities = data.capabilities;
        }
        if (data.modelName) {
          this.currentModel = data.modelName;
        }
        pendingRequest.resolve(data);
      } else {
        pendingRequest.reject(new Error(error || 'Worker request failed'));
      }
    }
  }

  private handleWorkerError(error: ErrorEvent): void {
    console.error('Client LLM Worker error:', error);
    this.markLocalFailure(`Worker error occurred: ${error.message || 'unknown worker error'}`);
    // Reject all pending requests
    for (const [id, request] of this.pendingRequests.entries()) {
      request.reject(new Error('Worker error occurred'));
      this.pendingRequests.delete(id);
    }
  }

  private async sendWorkerRequest(type: string, data: any, timeoutMs?: number): Promise<any> {
    if (!this.worker) {
      throw new Error('Worker not available');
    }

    return new Promise((resolve, reject) => {
      const id = `req_${++this.requestCounter}`;
      const effectiveTimeout = timeoutMs ?? (type === 'initialize' || type === 'switchModel' ? 900000 : LLM_CONFIG.LOCAL_GENERATION_TIMEOUT_MS);
      const startedAt = performance.now();

      // Extended timeout for model loading and large model inference
      const timeout = setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          const message = `Worker request timeout during ${type} after ${effectiveTimeout}ms`;
          this.emitServiceDiagnostic('worker:request_timeout', { requestId: id, requestType: type, timeoutMs: effectiveTimeout });
          if (type === 'generate' || type === 'probe') {
            this.resetLocalWorker(message);
          }
          reject(new Error(message));
        }
      }, effectiveTimeout);

      const originalResolve = resolve;
      const originalReject = reject;

      // Wrap resolve/reject to clear timeout
      this.pendingRequests.set(id, {
        type,
        startedAt,
        timeoutMs: effectiveTimeout,
        resolve: (result: any) => {
          clearTimeout(timeout);
          const durationMs = Math.round(performance.now() - startedAt);
          this.emitServiceDiagnostic('worker:request_success', { requestId: id, requestType: type, durationMs });
          originalResolve(result);
        },
        reject: (error: any) => {
          clearTimeout(timeout);
          const durationMs = Math.round(performance.now() - startedAt);
          this.emitServiceDiagnostic('worker:request_failed', {
            requestId: id,
            requestType: type,
            durationMs,
            error: error instanceof Error ? error.message : String(error),
          });
          originalReject(error);
        }
      });

      this.worker!.postMessage({ id, type, data });
    });
  }

  private markLocalFailure(reason: string): void {
    this.localGenerationUnhealthy = true;
    this.localHealth = {
      ...this.localHealth,
      state: 'unhealthy',
      proven: false,
      lastFailureAt: new Date().toISOString(),
      lastFailureReason: reason,
      consecutiveFailures: this.localHealth.consecutiveFailures + 1,
    };
    this.localRetryAfter = Date.now() + LLM_CONFIG.LOCAL_RETRY_COOLDOWN_MS;
    this.emitServiceDiagnostic('local:marked_unhealthy', {
      reason,
      retryAfter: new Date(this.localRetryAfter).toISOString(),
    });
  }

  private markLocalSuccess(durationMs?: number): void {
    this.localGenerationUnhealthy = false;
    this.localHealth = {
      ...this.localHealth,
      state: 'ready',
      proven: true,
      lastSuccessAt: new Date().toISOString(),
      lastGenerationDurationMs: durationMs ?? this.localHealth.lastGenerationDurationMs,
      consecutiveFailures: 0,
    };
    this.localRetryAfter = 0;
    this.emitServiceDiagnostic('local:marked_ready', { durationMs });
  }

  private resetLocalWorker(reason: string): void {
    this.markLocalFailure(reason);

    if (this.worker) {
      this.worker.terminate();
      this.worker = null;
    }

    for (const [id, request] of this.pendingRequests.entries()) {
      request.reject(new Error(`Worker reset after ${request.type}: ${reason}`));
      this.pendingRequests.delete(id);
    }

    this.isInitialized = false;
    this.isInitializing = false;
    this.backgroundWarmupPromise = null;
    this.localProbePromise = null;
    this.initializeWorker();
  }

  async initialize(modelName: string = LLM_CONFIG.CLIENT_MODEL): Promise<void> {
    if (this.isInitialized && this.currentModel === modelName) {
      return;
    }

    if (this.isInitializing) {
      // Wait for existing initialization to complete
      while (this.isInitializing) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      return;
    }

    this.isInitializing = true;
    this.localHealth.state = 'loading';
    this.emitServiceDiagnostic('local:initialize_start', { requestedModel: modelName });

    try {
      const result = await this.sendWorkerRequest('initialize', { modelName });
      this.isInitialized = true;
      this.currentModel = result.modelName;
      this.capabilities = result.capabilities;
      this.localHealth.state = 'loaded_unprobed';
      console.log(`Client LLM Worker initialized with ${result.modelName}`);
      this.emitServiceDiagnostic('local:initialize_success', { modelName: result.modelName, capabilities: result.capabilities });
    } catch (error) {
      console.error('Failed to initialize Client LLM Worker:', error);
      this.markLocalFailure(error instanceof Error ? error.message : String(error));
      throw error;
    } finally {
      this.isInitializing = false;
    }
  }

  async switchModel(modelName: string): Promise<void> {
    if (this.currentModel === modelName && this.isInitialized) {
      return; // Already using this model
    }

    try {
      const result = await this.sendWorkerRequest('switchModel', { modelName });
      this.currentModel = result.modelName;
      this.capabilities = result.capabilities;
      this.isInitialized = true;
      this.localHealth.state = 'loaded_unprobed';
      this.localHealth.proven = false;
      this.localGenerationUnhealthy = false;
      console.log(`Switched to model: ${result.modelName}`);
    } catch (error) {
      console.error('Failed to switch model:', error);
      this.markLocalFailure(error instanceof Error ? error.message : String(error));
      throw error;
    }
  }

  async generateText(prompt: string, maxTokens: number = 50): Promise<string> {
    const cloudConfigured = openRouterLLMService.isConfigured();
    const boundedMaxTokens = Math.min(maxTokens, LLM_CONFIG.LOCAL_MAX_NEW_TOKENS);

    if (this.localGenerationUnhealthy && cloudConfigured && Date.now() < this.localRetryAfter) {
      this.emitServiceDiagnostic('route:cloud_after_prior_local_failure', {
        reason: this.localHealth.lastFailureReason || 'local generation is in cooldown after a prior failure',
        promptLength: prompt.length,
        maxTokens: boundedMaxTokens,
      });
      return this.generateWithOpenRouter(prompt, boundedMaxTokens);
    }

    if (prompt.length > LLM_CONFIG.LOCAL_MAX_PROMPT_CHARS) {
      const reason = `Local prompt budget exceeded: ${prompt.length} chars > ${LLM_CONFIG.LOCAL_MAX_PROMPT_CHARS} chars.`;
      this.emitServiceDiagnostic('local:prompt_budget_exceeded', {
        promptLength: prompt.length,
        maxPromptChars: LLM_CONFIG.LOCAL_MAX_PROMPT_CHARS,
        maxTokens: boundedMaxTokens,
      });
      if (cloudConfigured) {
        return this.generateWithOpenRouter(prompt, boundedMaxTokens);
      }
      throw new Error(`${reason} Compact the GraphRAG context or configure OpenRouter as last-resort fallback.`);
    }

    if (!this.isInitialized) {
      await this.initialize();
    }

    if (!this.localHealth.proven) {
      const probeOk = await this.probeLocalInference();
      if (!probeOk && cloudConfigured) {
        this.emitServiceDiagnostic('route:cloud_after_probe_failed', { promptLength: prompt.length, maxTokens: boundedMaxTokens });
        return this.generateWithOpenRouter(prompt, boundedMaxTokens);
      }
      if (!probeOk) {
        const fallbackStatus = openRouterLLMService.getConfigurationStatus();
        throw new Error(
          `Local LiquidAI generation probe failed, and cloud fallback is unavailable: ${fallbackStatus.reason}`,
        );
      }
    }

    try {
      const startedAt = performance.now();
      const localTimeoutMs = cloudConfigured
        ? Math.max(
            1,
            Math.min(
              LLM_CONFIG.LOCAL_GENERATION_TIMEOUT_MS,
              LLM_CONFIG.LOCAL_GENERATION_FALLBACK_MS,
            ),
          )
        : LLM_CONFIG.LOCAL_GENERATION_TIMEOUT_MS;

      if (cloudConfigured && localTimeoutMs < LLM_CONFIG.LOCAL_GENERATION_TIMEOUT_MS) {
        this.emitServiceDiagnostic('local:soft_timeout_enabled', {
          localTimeoutMs,
          hardTimeoutMs: LLM_CONFIG.LOCAL_GENERATION_TIMEOUT_MS,
          promptLength: prompt.length,
        });
      }

      const result = await this.sendWorkerRequest(
        'generate',
        { prompt, maxTokens: boundedMaxTokens },
        localTimeoutMs,
      );
      this.markLocalSuccess(Math.round(performance.now() - startedAt));
      return result.text;
    } catch (error) {
      console.error('Text generation failed:', error);
      this.markLocalFailure(error instanceof Error ? error.message : String(error));
      if (cloudConfigured) {
        console.warn('Using OpenRouter fallback after local generation failure');
        this.emitServiceDiagnostic('route:cloud_after_local_failure', {
          promptLength: prompt.length,
          maxTokens: boundedMaxTokens,
          error: error instanceof Error ? error.message : String(error),
        });
        return this.generateWithOpenRouter(prompt, boundedMaxTokens);
      }
      const fallbackStatus = openRouterLLMService.getConfigurationStatus();
      console.warn('OpenRouter fallback unavailable after local generation failure:', fallbackStatus);
      throw new Error(
        `Local LiquidAI generation failed, and cloud fallback is unavailable: ${fallbackStatus.reason}`,
      );
    }
  }

  async probeLocalInference(options: { force?: boolean } = {}): Promise<boolean> {
    if (this.localProbePromise && !options.force) {
      return this.localProbePromise;
    }

    this.localProbePromise = (async () => {
      if (!this.worker) {
        this.markLocalFailure('Worker not available for local inference probe.');
        return false;
      }

      if (this.localHealth.state === 'unhealthy' && !options.force && Date.now() < this.localRetryAfter) {
        this.emitServiceDiagnostic('probe:skipped_cooldown', {
          retryAfter: new Date(this.localRetryAfter).toISOString(),
        });
        return false;
      }

      try {
        if (!this.isInitialized) {
          await this.initialize(this.currentModel || LLM_CONFIG.CLIENT_MODEL);
        }

        this.localHealth.state = 'probing';
        this.localHealth.lastProbeAt = new Date().toISOString();
        this.emitServiceDiagnostic('probe:start', { timeoutMs: LLM_CONFIG.LOCAL_PROBE_TIMEOUT_MS });
        const result = await this.sendWorkerRequest(
          'probe',
          { maxTokens: LLM_CONFIG.LOCAL_PROBE_MAX_TOKENS },
          LLM_CONFIG.LOCAL_PROBE_TIMEOUT_MS,
        );
        const durationMs = Number(result.durationMs || 0);
        this.localHealth.lastProbeDurationMs = durationMs;
        this.markLocalSuccess(durationMs);
        this.emitServiceDiagnostic('probe:success', {
          durationMs,
          text: String(result.text || '').slice(0, 120),
        });
        return true;
      } catch (error) {
        const reason = error instanceof Error ? error.message : String(error);
        this.markLocalFailure(reason);
        this.emitServiceDiagnostic('probe:failed', { reason });
        return false;
      } finally {
        this.localProbePromise = null;
      }
    })();

    return this.localProbePromise;
  }

  async getCapabilities(): Promise<any> {
    try {
      return await this.sendWorkerRequest('getCapabilities', {});
    } catch (error) {
      console.error('Failed to get capabilities:', error);
      return { webGPU: false, simd: false, currentModel: this.currentModel, isInitialized: false };
    }
  }

  getCurrentModel(): string {
    return this.currentModel;
  }

  getStatus(): {
    isInitialized: boolean;
    isInitializing: boolean;
    hasWorker: boolean;
    currentModel: string;
    capabilities: any;
    localHealth: LocalInferenceHealth;
    cloudFallback: ReturnType<typeof openRouterLLMService.getConfigurationStatus>;
    retryAfter?: string;
  } {
    return {
      isInitialized: this.isInitialized,
      isInitializing: this.isInitializing,
      hasWorker: this.worker !== null,
      currentModel: this.currentModel,
      capabilities: this.capabilities,
      localHealth: { ...this.localHealth },
      cloudFallback: openRouterLLMService.getConfigurationStatus(),
      retryAfter: this.localRetryAfter ? new Date(this.localRetryAfter).toISOString() : undefined,
    };
  }

  isCloudFallbackAvailable(): boolean {
    return openRouterLLMService.isConfigured();
  }

  getCloudFallbackStatus(): { configured: boolean; reason: string; baseUrl: string; directOpenRouter: boolean } {
    return openRouterLLMService.getConfigurationStatus();
  }

  private generateWithOpenRouter(prompt: string, maxTokens: number): Promise<string> {
    return openRouterLLMService.generateText(prompt, {
      maxTokens,
      model: this.getOpenRouterModelForCurrentLocalModel(),
      temperature: this.currentModel.includes('Thinking') ? 0.1 : 0.1,
      topP: this.currentModel.includes('Thinking') ? 0.1 : undefined,
      topK: 50,
      repetitionPenalty: 1.05,
    });
  }

  warmLocalModelInBackground(options: { force?: boolean } = {}): void {
    if ((!options.force && this.localHealth.state === 'unhealthy' && Date.now() < this.localRetryAfter) || this.isInitializing || this.backgroundWarmupPromise) {
      return;
    }

    if (this.isInitialized && this.localHealth.proven && !options.force) {
      return;
    }

    this.backgroundWarmupPromise = this.initialize(this.currentModel || LLM_CONFIG.CLIENT_MODEL)
      .then(() => this.probeLocalInference({ force: options.force }))
      .then((ok) => {
        if (!ok) {
          throw new Error(this.localHealth.lastFailureReason || 'Local inference probe failed.');
        }
      })
      .catch((error) => {
        console.warn('Background local LLM warmup failed; cloud fallback remains available if configured', error);
      })
      .finally(() => {
        this.backgroundWarmupPromise = null;
      });
  }

  private getOpenRouterModelForCurrentLocalModel(): string {
    if (this.currentModel.includes('Thinking')) {
      return LLM_CONFIG.OPENROUTER_THINKING_MODEL;
    }
    return LLM_CONFIG.OPENROUTER_DEFAULT_MODEL;
  }

  // Enhanced conversation generation for different character types
  async generateConversationMessage(
    characterName: string,
    identity: string,
    conversationHistory: string[],
    type: 'start' | 'continue' | 'leave',
    otherCharacterName?: string
  ): Promise<string> {
    let prompt = '';
    const isInstructModel = this.currentModel.includes('Instruct');

    if (isInstructModel) {
      // Optimized prompt format for instruction-tuned chat models
      prompt = `You are ${characterName}. ${identity}

Character context: You are a thoughtful character in a virtual town simulation. Respond naturally and stay in character.

`;
    } else {
      // Format for conversation models
      prompt = `${characterName} is ${identity.toLowerCase()}

`;
    }

    if (type === 'start') {
      if (isInstructModel) {
        prompt += `Task: Start a conversation with ${otherCharacterName}. Introduce yourself naturally and start a friendly dialogue.

Response:`;
      } else {
        prompt += `${characterName} walks up to ${otherCharacterName} and says: "`;
      }
    } else if (type === 'continue') {
      if (isInstructModel) {
        prompt += `Conversation so far:
${conversationHistory.slice(-3).join('\n')}

Task: Continue this conversation naturally as ${characterName}.

Response:`;
      } else {
        prompt += conversationHistory.slice(-2).join('\n') + `\n${characterName}: "`;
      }
    } else if (type === 'leave') {
      if (isInstructModel) {
        prompt += `Conversation so far:
${conversationHistory.slice(-2).join('\n')}

Task: Politely end this conversation as ${characterName}.

Response:`;
      } else {
        prompt += conversationHistory.slice(-2).join('\n') + `\n${characterName} needs to leave and says: "`;
      }
    }

    const maxTokens = type === 'start' ? 60 : type === 'leave' ? 40 : 80;
    let response = await this.generateText(prompt, maxTokens);
    
    // Clean up response based on model type
    if (!isInstructModel && !response.endsWith('"')) {
      // Add closing quote for conversation models
      response = response.split('"')[0] + '"';
    }
    
    // Remove character name prefixes and clean up
    response = this.cleanResponse(response, characterName, otherCharacterName);
    
    return response;
  }

  private cleanResponse(response: string, characterName: string, otherCharacterName?: string): string {
    // Remove any character name prefixes that might have been generated
    response = response.replace(new RegExp(`^${characterName}:?\\s*`, 'i'), '');
    if (otherCharacterName) {
      response = response.replace(new RegExp(`^${otherCharacterName}:?\\s*`, 'i'), '');
    }
    
    // Remove quotes that were part of prompt format
    response = response.replace(/^["']|["']$/g, '');
    
    // Remove conversation formatting artifacts
    response = response.replace(/^\s*says?:?\s*/i, '');
    
    // Clean up and limit length
    response = response.trim().substring(0, 200);
    
    // Ensure proper sentence ending
    if (response && !response.match(/[.!?]$/)) {
      response += '.';
    }
    
    return response || "Hello there!";
  }

  destroy(): void {
    if (this.worker) {
      this.worker.terminate();
      this.worker = null;
    }
    this.isInitialized = false;
    this.isInitializing = false;
    this.pendingRequests.clear();
  }
}

// Create singleton instance
export const clientLLMWorkerService = new ClientLLMWorkerService();
