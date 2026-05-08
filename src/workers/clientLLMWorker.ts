// Web Worker for Client-side LLM processing to prevent blocking the main thread
import { suppressWebGPUWarnings } from '../lib/warningSuppressionUtils';
import { SUPPORTED_MODELS } from '../lib/llmConfig';

// Use centralized model configuration
const supportedModels = SUPPORTED_MODELS;

let textGenerator: any = null;
let isInitialized = false;
let isInitializing = false; // Add lock to prevent simultaneous initializations
let currentModelName = '';
let webGPUSupported = false;
let simdSupported = false;
let transformersPromise: Promise<{ pipeline: any; env: any }> | null = null;
const progressMilestones = new Map<string, number>();

// Global WebGPU detection cache to prevent repeated adapter requests
let webGPUDetectionCache: { result: boolean; timestamp: number; } | null = null;
const WEBGPU_CACHE_DURATION = 5 * 60 * 1000; // 5 minutes cache duration

async function getTransformers() {
  if (!transformersPromise) {
    transformersPromise = (async () => {
      const transformers = await import('@huggingface/transformers');
      transformers.env.allowLocalModels = false;
      transformers.env.useBrowserCache = true;
      return { pipeline: transformers.pipeline, env: transformers.env };
    })();
  }
  return transformersPromise;
}

// Worker message types
interface WorkerRequest {
  id: string;
  type: 'initialize' | 'generate' | 'getCapabilities' | 'switchModel';
  data: any;
}

interface WorkerResponse {
  id: string;
  success: boolean;
  data?: any;
  error?: string;
}

function emitDiagnostic(event: string, data: Record<string, unknown> = {}, requestId?: string) {
  const payload = {
    event,
    timestamp: new Date().toISOString(),
    modelName: currentModelName || data.modelName,
    requestId,
    ...data,
  };
  console.log(`[Worker][LLM] ${event}`, payload);
  self.postMessage({ id: `diag_${Date.now()}_${Math.random().toString(36).slice(2)}`, success: true, data: { diagnostic: payload } });
}

function emitProgress(info: any, requestId?: string) {
  const payload = {
    requestId,
    status: info?.status,
    name: info?.name,
    file: info?.file,
    progress: info?.progress,
    loaded: info?.loaded,
    total: info?.total,
  };
  const progressKey = `${requestId || 'global'}:${payload.file || payload.name || payload.status || 'unknown'}`;

  if (payload.status === 'progress' || payload.status === 'progress_total') {
    const progress = Number(payload.progress || 0);
    const milestone = Math.min(100, Math.floor(progress / 5) * 5);
    const lastMilestone = progressMilestones.get(progressKey);
    if (lastMilestone === milestone && progress < 100) {
      return;
    }
    progressMilestones.set(progressKey, milestone);
    console.log(`[Worker][LLM] download ${payload.file || payload.name || 'total'}: ${progress.toFixed(1)}%`);
  } else {
    console.log(`[Worker][LLM] ${payload.status}`, payload);
    if (payload.status === 'done' && payload.file) {
      progressMilestones.delete(progressKey);
    }
  }
  self.postMessage({ id: `progress_${Date.now()}_${Math.random().toString(36).slice(2)}`, success: true, data: { progress: payload } });
}

// Detect backend capabilities in worker
async function detectCapabilities() {
  try {
    // Check WebGPU support with actual device creation test
    webGPUSupported = await testWebGPUSupport();
    
    // Check SIMD support (WebAssembly SIMD)
    simdSupported = typeof WebAssembly !== 'undefined' && 
                   WebAssembly.validate(new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0]));
    
    console.log(`[Worker] Capabilities detected - WebGPU: ${webGPUSupported}, SIMD: ${simdSupported}`);
    
    return { webGPU: webGPUSupported, simd: simdSupported };
  } catch (error) {
    console.warn('[Worker] Error detecting capabilities:', error);
    return { webGPU: false, simd: false };
  }
}

// Test WebGPU support with actual device creation
async function testWebGPUSupport(): Promise<boolean> {
  // Check cache first
  if (webGPUDetectionCache) {
    const now = Date.now();
    if (now - webGPUDetectionCache.timestamp < WEBGPU_CACHE_DURATION) {
      return webGPUDetectionCache.result;
    }
  }

  // Perform detection with warning suppression
  const result = await suppressWebGPUWarnings(async () => {
    try {
      if (!('gpu' in navigator) || typeof (navigator as any).gpu?.requestAdapter !== 'function') {
        return false;
      }
      
      const adapter = await (navigator as any).gpu.requestAdapter({
        powerPreference: 'high-performance'
      });
      
      if (!adapter) {
        return false;
      }
      
      // Try to create a device to ensure WebGPU is actually functional
      try {
        const device = await adapter.requestDevice();
        if (device && device.queue) {
          device.destroy?.(); // Clean up the test device
          return true;
        }
        // If device exists but doesn't have queue, it's not functional
        device?.destroy?.();
        return false;
      } catch (deviceError) {
        // Only log device errors that aren't experimental warnings
        if (!deviceError || !String(deviceError).includes('experimental')) {
          console.warn('[Worker] WebGPU device creation failed:', deviceError);
        }
        return false;
      }
    } catch (error) {
      // Only log errors that aren't experimental warnings
      if (!error || !String(error).includes('experimental')) {
        console.warn('[Worker] WebGPU detection failed:', error);
      }
      return false;
    }
  });

  // Cache the result
  webGPUDetectionCache = {
    result,
    timestamp: Date.now()
  };

  return result;
}

// Configure transformers.js environment for optimal performance
async function configureEnvironment(modelName: string) {
  const { env } = await getTransformers();
  const modelConfig = supportedModels[modelName as keyof typeof SUPPORTED_MODELS];
  if (!modelConfig) {
    throw new Error(`Unsupported model: ${modelName}`);
  }

  try {
    // Configure ONNX Runtime directly to suppress warnings for large models
    if (typeof (self as any).ort !== 'undefined') {
      const ort = (self as any).ort;
      if (ort.env) {
        try {
          // Comprehensive warning suppression for ONNX Runtime
          ort.env.logLevel = 'error'; // Only show errors, suppress warnings
          ort.env.logVerbosityLevel = 0; // Minimize verbose logging
          
          // Additional ONNX Runtime warning suppressions
          if (ort.env.webgl2) {
            ort.env.webgl2.enableWarningCapture = false;
          }
          
          // Configure for large model performance
          if (ort.env.webgpu && modelConfig.requiresWebGPU && webGPUSupported) {
            ort.env.webgpu.validateInputContent = false;
            ort.env.webgpu.contextTimeoutMs = 15000; // Extended timeout for large models
            ort.env.webgpu.powerPreference = 'high-performance';
            ort.env.webgpu.forceFallbackAdapter = false; // Use dedicated GPU when available
            ort.env.webgpu.enableDebugInfo = false; // Disable debug output
          }
          
          if (ort.env.wasm) {
            ort.env.wasm.numThreads = Math.min(navigator.hardwareConcurrency || 4, 8);
            ort.env.wasm.simd = simdSupported;
            ort.env.wasm.enableExperimentalFeatures = false; // Disable experimental warnings
          }
          
          console.log('[Worker] ONNX Runtime configured with comprehensive warning suppression');
        } catch (ortError) {
          console.log('[Worker] ONNX Runtime direct configuration not available:', ortError);
        }
      }
    }

    // Configure WebGPU if available and required
    if (modelConfig.requiresWebGPU && webGPUSupported) {
      try {
        // Enable WebGPU backend if available in this version
        if ((env.backends as any).webgpu) {
          (env.backends as any).webgpu.enabled = true;
          console.log('[Worker] WebGPU backend enabled');
        } else {
          console.log('[Worker] WebGPU backend flag not exposed; continuing with device="webgpu"');
        }
      } catch (e) {
        console.log('[Worker] WebGPU configuration not available');
      }
    }

    // Configure WASM with SIMD and threading optimizations
    if (env.backends.onnx?.wasm) {
      // Enable SIMD if supported
      if (simdSupported && modelConfig.simdOptimized) {
        try {
          (env.backends.onnx.wasm as any).simd = true;
          console.log('[Worker] WASM SIMD enabled');
        } catch (e) {
          console.log('[Worker] SIMD configuration not available');
        }
      }

      // Configure threading
      const numThreads = Math.min(navigator.hardwareConcurrency || 4, 8);
      try {
        (env.backends.onnx.wasm as any).numThreads = numThreads;
        console.log(`[Worker] Using ${numThreads} threads`);
      } catch (e) {
        console.log('[Worker] Thread configuration not available');
      }

      // Memory optimization for large models
      if (modelConfig.size.includes('GB')) {
        try {
          (env.backends.onnx.wasm as any).memoryLimitMB = 8192; // Increased limit for large models
          console.log('[Worker] Memory limit set for large model');
        } catch (e) {
          console.log('[Worker] Memory configuration not available');
        }
      }
    }

    // Set cache directory optimization
    env.cacheDir = './.cache/transformers';

  } catch (error) {
    console.warn('[Worker] Environment configuration error:', error);
    // Continue with default configuration
  }
}

// Initialize the LLM model with optimizations
async function initializeLLM(modelName: string = 'LiquidAI/LFM2.5-1.2B-Instruct-ONNX', requestId?: string): Promise<void> {
  if (isInitialized && textGenerator && currentModelName === modelName) {
    return;
  }

  // Prevent simultaneous initialization attempts
  if (isInitializing) {
    console.log('[Worker] Initialization already in progress, waiting...');
    // Wait for current initialization to complete
    while (isInitializing) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    return;
  }

  isInitializing = true;

  try {
    // Clear previous model if switching
    if (textGenerator && currentModelName !== modelName) {
      textGenerator.dispose?.();
      textGenerator = null;
      isInitialized = false;
    }

    const { pipeline, env } = await getTransformers();
    emitDiagnostic('initialize:start', { modelName }, requestId);
    await detectCapabilities();
    await configureEnvironment(modelName);
    
    const modelConfig = supportedModels[modelName as keyof typeof SUPPORTED_MODELS];
    emitDiagnostic('initialize:capabilities', {
      modelName,
      webGPU: webGPUSupported,
      simd: simdSupported,
      modelConfig,
      transformersVersion: (env as any).version,
    }, requestId);
    
    // Check hardware compatibility
    if (modelConfig?.requiresWebGPU && !webGPUSupported) {
      throw new Error(`Model ${modelName} requires WebGPU but it's not available. Consider using a lighter model.`);
    }

    // Initialize with optimized configuration
    const pipelineOptions: any = {
      progress_callback: (info: any) => emitProgress(info, requestId),
      // Configure session options to optimize for large models
      session_options: {
        // Suppress ONNX Runtime warnings about unused initializers  
        log_severity_level: 3, // Only errors (suppress warnings)
        log_verbosity_level: 0, // Minimal logging
        
        // Optimize memory for large models
        enable_mem_pattern: false, // Disable memory pattern optimization for large models
        enable_cpu_mem_arena: false, // Use system allocator for large models
        
        // Graph optimizations - balance performance vs memory
        graph_optimization_level: 'basic', // Use basic optimizations to avoid unnecessary warnings
        
        // Threading for large models
        intra_op_num_threads: Math.min(navigator.hardwareConcurrency || 4, 8),
        inter_op_num_threads: Math.min(navigator.hardwareConcurrency || 4, 4),
        
        // Enable profiling for debugging if needed (disabled by default)
        enable_profiling: false
      }
    };
    
    // Use quantization for smaller models or when WebGPU is not available
    // Set device preference with better error handling and large model optimizations
    if (modelConfig?.requiresWebGPU && webGPUSupported) {
      pipelineOptions.device = 'webgpu';
      pipelineOptions.dtype = (modelConfig as any)?.preferredDtype || 'q4'; // Quantized WebGPU path keeps browser memory pressure manageable.
      
      // Additional WebGPU optimizations for large models
      pipelineOptions.webgpu_options = {
        powerPreference: 'high-performance',
        forceFallbackAdapter: false,
        // Memory management for large models
        maxBindGroupsPerCommandEncoder: 64,
        maxBindingsPerBindGroup: 1000
      };
    } else {
      pipelineOptions.device = 'wasm';
      pipelineOptions.dtype = modelConfig?.quantized ? 'q8' : undefined;
      
      // WASM optimizations for large models  
      pipelineOptions.wasm_options = {
        numThreads: Math.min(navigator.hardwareConcurrency || 4, 8),
        simd: simdSupported
      };
    }

    try {
      emitDiagnostic('pipeline:create', {
        modelName,
        device: pipelineOptions.device,
        dtype: pipelineOptions.dtype,
      }, requestId);
      textGenerator = await pipeline('text-generation', modelName, pipelineOptions);
      isInitialized = true;
      currentModelName = modelName;
      emitDiagnostic('initialize:success', {
        modelName,
        device: pipelineOptions.device,
        dtype: pipelineOptions.dtype,
      }, requestId);
    } catch (pipelineError) {
      emitDiagnostic('pipeline:create_failed', {
        modelName,
        device: pipelineOptions.device,
        error: pipelineError instanceof Error ? pipelineError.message : String(pipelineError),
      }, requestId);
      
      // If WebGPU pipeline fails, try WASM fallback
      if (pipelineOptions.device === 'webgpu') {
        console.log('[Worker] WebGPU pipeline failed, falling back to WASM...');
        const fallbackOptions = {
          ...pipelineOptions,
          device: 'wasm',
          dtype: 'q8',
        };
        delete fallbackOptions.webgpu_options;
        
        try {
          textGenerator = await pipeline('text-generation', modelName, fallbackOptions);
          isInitialized = true;
          currentModelName = modelName;
          emitDiagnostic('initialize:success_wasm_fallback', {
            modelName,
            device: fallbackOptions.device,
            dtype: fallbackOptions.dtype,
          }, requestId);
        } catch (fallbackError) {
          console.error('[Worker] WASM fallback also failed:', fallbackError);
          throw fallbackError;
        }
      } else {
        throw pipelineError;
      }
    }
    
  } catch (error) {
    console.error(`[Worker] Failed to initialize ${modelName}:`, error);
    const modelConfig = supportedModels[modelName as keyof typeof SUPPORTED_MODELS];

    // WebGPU-targeted Liquid models should fall through to the cloud fallback layer,
    // not silently become a tiny local GPT-2 model.
    if (modelConfig?.requiresWebGPU) {
      emitDiagnostic('initialize:failed_no_local_fallback', {
        modelName,
        error: error instanceof Error ? error.message : String(error),
      }, requestId);
      throw error;
    }
    
    // Fallback to smaller model if initialization fails
    if (modelName !== 'Xenova/distilgpt2') {
      console.log('[Worker] Falling back to DistilGPT-2...');
      isInitializing = false; // Reset lock before recursive call
      return initializeLLM('Xenova/distilgpt2', requestId);
    }
    
    throw error;
  } finally {
    isInitializing = false;
  }
}

// Generate text using the LLM with model-specific optimizations
async function generateText(prompt: string, maxTokens: number = 50, requestId?: string): Promise<string> {
  if (!textGenerator || !isInitialized) {
    throw new Error('LLM not initialized');
  }

  try {
    const modelConfig = supportedModels[currentModelName as keyof typeof SUPPORTED_MODELS];
    const isInstructModel = currentModelName.includes('Instruct') ||
                           currentModelName.includes('Thinking') ||
                           modelConfig?.type === 'instruct';
    
    // Format prompt appropriately for instruction models
    let formattedPrompt: string | Array<{ role: string; content: string }> = prompt;
    
    if (isInstructModel) {
      formattedPrompt = [
        { role: 'system', content: 'You are a concise, helpful assistant.' },
        { role: 'user', content: prompt },
      ];
    }

    // Model-specific generation parameters
    const generationConfig: any = {
      max_new_tokens: maxTokens,
      do_sample: true,
    };
    const padTokenId = (modelConfig as any)?.padTokenId;
    if (padTokenId !== undefined) {
      generationConfig.pad_token_id = padTokenId;
    } else if (!isInstructModel) {
      generationConfig.pad_token_id = 50256;
    } else if (currentModelName.includes('Llama')) {
      generationConfig.pad_token_id = 128001;
    }

    // Configure generation parameters based on model type
    if (isInstructModel) {
      // Optimized settings for instruction-tuned models
      generationConfig.temperature = 0.1;
      if (currentModelName.includes('Thinking')) {
        generationConfig.top_p = 0.1;
      }
      generationConfig.repetition_penalty = 1.05;
      generationConfig.top_k = 50;
    } else {
      // Settings for conversation models like DistilGPT-2
      generationConfig.temperature = 0.7;
      generationConfig.top_p = 0.9;
      generationConfig.repetition_penalty = 1.1;
    }

    // Use WebGPU-optimized generation if available
    if (modelConfig?.requiresWebGPU && webGPUSupported) {
      generationConfig.use_cache = true; // Enable KV cache for better performance
    }

    emitDiagnostic('generate:start', {
      modelName: currentModelName,
      promptLength: prompt.length,
      maxTokens,
      isInstructModel,
      webGPU: webGPUSupported,
      device: modelConfig?.requiresWebGPU && webGPUSupported ? 'webgpu' : 'wasm',
      stopTokens: (modelConfig as any)?.stopTokens,
    }, requestId);

    const result = await textGenerator(formattedPrompt as any, generationConfig);

    // Extract and clean generated text
    let newText = extractGeneratedText(result, formattedPrompt);
    
    // Clean up instruction model responses
    newText = newText
      .trim();
    for (const token of ((modelConfig as any)?.stopTokens || ['<|im_end|>', '<|eot_id|>'])) {
      newText = newText.split(token)[0].trim();
    }
    
    // Remove potential repetition or incomplete sentences for better quality
    newText = cleanGeneratedText(newText);
    
    emitDiagnostic('generate:success', {
      modelName: currentModelName,
      outputLength: newText.length,
    }, requestId);

    return newText;
  } catch (error) {
    console.error('[Worker] Text generation failed:', error);
    throw error;
  }
}

function extractGeneratedText(result: any, formattedPrompt: string | Array<{ role: string; content: string }>): string {
  const first = Array.isArray(result) ? result[0] : result;
  const generated = first?.generated_text;

  if (Array.isArray(generated)) {
    const lastMessage = generated[generated.length - 1];
    return String(lastMessage?.content || '').trim();
  }

  const fullText = String(generated || '');
  if (typeof formattedPrompt === 'string' && fullText.startsWith(formattedPrompt)) {
    return fullText.slice(formattedPrompt.length).trim();
  }
  return fullText.trim();
}

// Clean and optimize generated text
function cleanGeneratedText(text: string): string {
  // Remove excessive repetition
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
  
  // Remove duplicate consecutive sentences
  const uniqueSentences = [];
  let lastSentence = '';
  
  for (const sentence of sentences) {
    const trimmed = sentence.trim();
    if (trimmed !== lastSentence && trimmed.length > 3) {
      uniqueSentences.push(trimmed);
      lastSentence = trimmed;
    }
    if (uniqueSentences.length >= 3) break; // Limit response length
  }
  
  let result = uniqueSentences.join('. ');
  if (result && !result.match(/[.!?]$/)) {
    result += '.';
  }
  
  return result.substring(0, 200).trim() || "I understand.";
}

// Handle model switching
async function switchModel(modelName: string, requestId?: string): Promise<void> {
  if (!(modelName in supportedModels)) {
    throw new Error(`Unsupported model: ${modelName}`);
  }

  if (currentModelName === modelName && textGenerator && isInitialized) {
    return; // Already using this model
  }

  // Clear current model
  if (textGenerator) {
    textGenerator.dispose?.();
    textGenerator = null;
    isInitialized = false;
  }

  // Initialize new model
  await initializeLLM(modelName, requestId);
}

// Handle messages from the main thread with enhanced functionality
self.onmessage = async (event: MessageEvent<WorkerRequest>) => {
  const { id, type, data } = event.data;
  
  try {
    let responseData: any;
    
    switch (type) {
      case 'initialize':
        await initializeLLM(data.modelName, id);
        responseData = { 
          status: 'initialized', 
          modelName: currentModelName,
          capabilities: { webGPU: webGPUSupported, simd: simdSupported }
        };
        break;
        
      case 'generate':
        responseData = { text: await generateText(data.prompt, data.maxTokens, id) };
        break;

      case 'switchModel':
        await switchModel(data.modelName, id);
        responseData = { 
          status: 'switched', 
          modelName: currentModelName,
          capabilities: { webGPU: webGPUSupported, simd: simdSupported }
        };
        break;

      case 'getCapabilities':
        await detectCapabilities();
        responseData = { 
          webGPU: webGPUSupported, 
          simd: simdSupported,
          currentModel: currentModelName,
          supportedModels: Object.keys(supportedModels),
          isInitialized
        };
        break;
        
      default:
        throw new Error(`Unknown request type: ${type}`);
    }
    
    const response: WorkerResponse = {
      id,
      success: true,
      data: responseData,
    };
    
    self.postMessage(response);
    
  } catch (error) {
    const response: WorkerResponse = {
      id,
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
    
    self.postMessage(response);
  }
};

// Handle worker errors gracefully
self.onerror = (error) => {
  console.error('[Worker] Global error:', error);
};

self.onunhandledrejection = (event) => {
  console.error('[Worker] Unhandled promise rejection:', event.reason);
  event.preventDefault();
};

// Export for TypeScript
export {};
