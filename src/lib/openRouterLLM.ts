import { LLM_CONFIG } from './llmConfig';

type ChatRole = 'system' | 'user' | 'assistant';

export interface OpenRouterMessage {
  role: ChatRole;
  content: string;
}

export interface OpenRouterGenerateOptions {
  model?: string;
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  topK?: number;
  repetitionPenalty?: number;
  signal?: AbortSignal;
}

export class OpenRouterLLMService {
  getConfigurationStatus(): { configured: boolean; reason: string; baseUrl: string; directOpenRouter: boolean } {
    const baseUrl = LLM_CONFIG.OPENROUTER_BASE_URL;
    const directOpenRouter = baseUrl.includes('openrouter.ai');

    if (!LLM_CONFIG.OPENROUTER_ENABLED) {
      return { configured: false, reason: 'OpenRouter fallback is disabled by VITE_OPENROUTER_ENABLED=false.', baseUrl, directOpenRouter };
    }

    if (!baseUrl) {
      return { configured: false, reason: 'VITE_OPENROUTER_BASE_URL is empty.', baseUrl, directOpenRouter };
    }

    if (directOpenRouter && !LLM_CONFIG.OPENROUTER_API_KEY) {
      return {
        configured: false,
        reason: 'VITE_OPENROUTER_BASE_URL points directly at OpenRouter, but VITE_OPENROUTER_API_KEY is not set. For GitHub Pages, set VITE_OPENROUTER_BASE_URL to your proxy URL instead.',
        baseUrl,
        directOpenRouter,
      };
    }

    return { configured: true, reason: 'OpenRouter fallback is configured.', baseUrl, directOpenRouter };
  }

  isConfigured(): boolean {
    return this.getConfigurationStatus().configured;
  }

  getDefaultModel(preferThinking = false): string {
    return preferThinking
      ? LLM_CONFIG.OPENROUTER_THINKING_MODEL
      : LLM_CONFIG.OPENROUTER_DEFAULT_MODEL;
  }

  async generateText(
    prompt: string,
    options: OpenRouterGenerateOptions = {},
  ): Promise<string> {
    return this.generateChat(
      [
        { role: 'system', content: 'You are a concise, helpful assistant.' },
        { role: 'user', content: prompt },
      ],
      options,
    );
  }

  async generateChat(
    messages: OpenRouterMessage[],
    options: OpenRouterGenerateOptions = {},
  ): Promise<string> {
    if (!this.isConfigured()) {
      throw new Error(this.getConfigurationStatus().reason);
    }

    const response = await fetch(`${LLM_CONFIG.OPENROUTER_BASE_URL.replace(/\/$/, '')}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(LLM_CONFIG.OPENROUTER_API_KEY ? { Authorization: `Bearer ${LLM_CONFIG.OPENROUTER_API_KEY}` } : {}),
        ...(LLM_CONFIG.OPENROUTER_SITE_URL ? { 'HTTP-Referer': LLM_CONFIG.OPENROUTER_SITE_URL } : {}),
        ...(LLM_CONFIG.OPENROUTER_SITE_NAME ? { 'X-OpenRouter-Title': LLM_CONFIG.OPENROUTER_SITE_NAME } : {}),
      },
      body: JSON.stringify({
        model: options.model || this.getDefaultModel(),
        messages,
        max_tokens: options.maxTokens ?? 100,
        temperature: options.temperature ?? 0.1,
        top_p: options.topP,
        top_k: options.topK ?? 50,
        repetition_penalty: options.repetitionPenalty ?? 1.05,
      }),
      signal: options.signal,
    });

    if (!response.ok) {
      const body = await response.text().catch(() => '');
      throw new Error(`OpenRouter request failed (${response.status}): ${body.slice(0, 300)}`);
    }

    const payload = await response.json();
    const text = payload?.choices?.[0]?.message?.content;
    if (typeof text !== 'string' || !text.trim()) {
      throw new Error('OpenRouter returned an empty response.');
    }

    return this.cleanText(text);
  }

  private cleanText(text: string): string {
    return text
      .replace(/<\|[^>]+?\|>/g, '')
      .trim();
  }
}

export const openRouterLLMService = new OpenRouterLLMService();
