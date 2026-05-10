function getRuntimeOpenRouterBaseUrl(): string {
  if (import.meta.env.VITE_OPENROUTER_BASE_URL) {
    return import.meta.env.VITE_OPENROUTER_BASE_URL;
  }

  if (typeof window !== 'undefined') {
    const localOverride = window.localStorage.getItem('PORTLAND_OPENROUTER_BASE_URL');
    if (localOverride) {
      return localOverride;
    }

    // Production safety net for GitHub Pages builds that missed env injection.
    if (window.location.hostname === 'portland-laws.github.io') {
      return 'https://animegf.chat/api/openrouter';
    }
  }

  return '';
}

// Configuration for LLM inference mode with enhanced model support
export const LLM_CONFIG = {
  // Set to 'client' for browser-based inference, 'server' for traditional API-based inference
  INFERENCE_MODE: (import.meta.env.VITE_LLM_INFERENCE_MODE as 'client' | 'server') || 'client',
  
  // Client-side model configuration. Use LiquidAI locally when WebGPU is available;
  // the app can fall back to OpenRouter while this model downloads or when no GPU exists.
  CLIENT_MODEL: import.meta.env.VITE_CLIENT_LLM_MODEL || 'LiquidAI/LFM2.5-1.2B-Instruct-ONNX',
  
  // Show client LLM status in UI (development only)
  SHOW_CLIENT_STATUS: !!import.meta.env.VITE_SHOW_CLIENT_LLM_STATUS || import.meta.env.NODE_ENV === 'development',
  
  // Maximum number of requests to process concurrently
  MAX_CONCURRENT_REQUESTS: parseInt(import.meta.env.VITE_MAX_CLIENT_REQUESTS || '2'),
  
  // Request timeout in milliseconds - extended for large models
  REQUEST_TIMEOUT: parseInt(import.meta.env.VITE_CLIENT_REQUEST_TIMEOUT || '45000'),

  // Model download timeout for initial loading
  MODEL_DOWNLOAD_TIMEOUT: parseInt(import.meta.env.VITE_MODEL_DOWNLOAD_TIMEOUT || '120000'),

  // How long to wait for local generation before using OpenRouter when cloud fallback is configured.
  LOCAL_GENERATION_FALLBACK_MS: parseInt(import.meta.env.VITE_LOCAL_GENERATION_FALLBACK_MS || '15000'),

  // Hard caps for local inference health checks. These keep WebGPU/ORT hangs from
  // becoming user-visible chat hangs.
  LOCAL_GENERATION_TIMEOUT_MS: parseInt(import.meta.env.VITE_LOCAL_GENERATION_TIMEOUT_MS || '45000'),
  LOCAL_PROBE_TIMEOUT_MS: parseInt(import.meta.env.VITE_LOCAL_PROBE_TIMEOUT_MS || '30000'),
  LOCAL_PROBE_MAX_TOKENS: parseInt(import.meta.env.VITE_LOCAL_PROBE_MAX_TOKENS || '8'),
  LOCAL_RETRY_COOLDOWN_MS: parseInt(import.meta.env.VITE_LOCAL_RETRY_COOLDOWN_MS || '600000'),
  LOCAL_MAX_PROMPT_CHARS: parseInt(import.meta.env.VITE_LOCAL_MAX_PROMPT_CHARS || '2400'),
  LOCAL_MAX_NEW_TOKENS: parseInt(import.meta.env.VITE_LOCAL_MAX_NEW_TOKENS || '96'),
  // Require local inference to prove a minimum throughput before it becomes
  // the default route for chat responses.
  LOCAL_MIN_TOKENS_PER_SECOND: parseFloat(import.meta.env.VITE_LOCAL_MIN_TOKENS_PER_SECOND || '4'),
  LOCAL_PERF_SAMPLE_MIN_TOKENS: parseInt(import.meta.env.VITE_LOCAL_PERF_SAMPLE_MIN_TOKENS || '10'),
  LOCAL_PERF_BENCH_MAX_TOKENS: parseInt(import.meta.env.VITE_LOCAL_PERF_BENCH_MAX_TOKENS || '40'),
  LOCAL_PERF_BENCH_TIMEOUT_MS: parseInt(import.meta.env.VITE_LOCAL_PERF_BENCH_TIMEOUT_MS || '20000'),

  // Enable WebGPU acceleration when available
  ENABLE_WEBGPU: import.meta.env.VITE_ENABLE_WEBGPU !== 'false',

  // Enable SIMD optimizations
  ENABLE_SIMD: import.meta.env.VITE_ENABLE_SIMD !== 'false',

  // Preferred backend order
  BACKEND_PRIORITY: ['webgpu', 'wasm', 'javascript'] as const,

  // OpenRouter cloud fallback. In production, prefer pointing OPENROUTER_BASE_URL
  // at a same-origin proxy so the API key is not exposed in browser bundles.
  OPENROUTER_ENABLED: import.meta.env.VITE_OPENROUTER_ENABLED !== 'false',
  OPENROUTER_API_KEY: import.meta.env.VITE_OPENROUTER_API_KEY || '',
  OPENROUTER_BASE_URL: getRuntimeOpenRouterBaseUrl(),
  OPENROUTER_SITE_URL: import.meta.env.VITE_OPENROUTER_SITE_URL || (typeof window !== 'undefined' ? window.location.origin : ''),
  OPENROUTER_SITE_NAME: import.meta.env.VITE_OPENROUTER_SITE_NAME || 'Portland Laws',
  OPENROUTER_DEFAULT_MODEL: import.meta.env.VITE_OPENROUTER_DEFAULT_MODEL || 'liquid/lfm-2.5-1.2b-instruct:free',
  OPENROUTER_THINKING_MODEL: import.meta.env.VITE_OPENROUTER_THINKING_MODEL || 'liquid/lfm-2.5-1.2b-thinking:free',
} as const;

// Supported models with their configurations
export const SUPPORTED_MODELS = {
  'LiquidAI/LFM2.5-1.2B-Instruct-ONNX': {
    name: 'LFM2.5 1.2B Instruct',
    size: '1.1GB',
    requiresWebGPU: true,
    contextLength: 32768,
    description: 'LiquidAI instruction model exported for ONNX Runtime WebGPU',
    type: 'instruct',
    quantized: true,
    simdOptimized: true,
    preferredDtype: 'q4',
    padTokenId: undefined,
    stopTokens: ['<|im_end|>', '<|eot_id|>']
  },
  'LiquidAI/LFM2.5-1.2B-Thinking-ONNX': {
    name: 'LFM2.5 1.2B Thinking',
    size: '1.1GB',
    requiresWebGPU: true,
    contextLength: 32768,
    description: 'LiquidAI reasoning model with <think> traces, exported for WebGPU',
    type: 'instruct',
    quantized: true,
    simdOptimized: true,
    preferredDtype: 'q4',
    padTokenId: undefined,
    stopTokens: ['<|im_end|>', '<|eot_id|>']
  },
  'Xenova/distilgpt2': {
    name: 'DistilGPT-2',
    size: '82MB',
    requiresWebGPU: false,
    contextLength: 1024,
    description: 'Fast, lightweight model suitable for all devices',
    type: 'conversational',
    quantized: true,
    simdOptimized: true
  },
  'onnx-community/Llama-3.2-1B-Instruct-ONNX': {
    name: 'Llama 3.2 1B Instruct',
    size: '637MB', 
    requiresWebGPU: true,
    contextLength: 2048,
    description: 'High-quality instruction-following model (WebGPU required)',
    type: 'instruct',
    quantized: false,
    simdOptimized: true
  },
  'onnx-community/Llama-3.2-3B-Instruct-ONNX': {
    name: 'Llama 3.2 3B Instruct',
    size: '1.9GB',
    requiresWebGPU: true,
    contextLength: 2048,
    description: 'Advanced instruction model with superior reasoning (WebGPU + 8GB+ RAM)',
    type: 'instruct',
    quantized: false,
    simdOptimized: true
  },
  'Xenova/LaMini-GPT-774M': {
    name: 'LaMini-GPT 774M',
    size: '310MB',
    requiresWebGPU: false,
    contextLength: 1024,
    description: 'Medium-sized model with good performance balance',
    type: 'conversational',
    quantized: true,
    simdOptimized: true
  },
  'Xenova/gpt2': {
    name: 'GPT-2',
    size: '124MB',
    requiresWebGPU: false,
    contextLength: 1024,
    description: 'Classic GPT-2 model, reliable baseline',
    type: 'conversational',
    quantized: true,
    simdOptimized: true
  }
} as const;

// Device capability requirements
export const MODEL_REQUIREMENTS = {
  'LiquidAI/LFM2.5-1.2B-Instruct-ONNX': {
    minRAM: 4096, // MB
    minStorage: 1400, // MB
    requiresWebGPU: true,
    preferredCores: 4
  },
  'LiquidAI/LFM2.5-1.2B-Thinking-ONNX': {
    minRAM: 4096, // MB
    minStorage: 1400, // MB
    requiresWebGPU: true,
    preferredCores: 4
  },
  'onnx-community/Llama-3.2-3B-Instruct-ONNX': {
    minRAM: 8192, // MB
    minStorage: 2048, // MB
    requiresWebGPU: true,
    preferredCores: 8
  },
  'onnx-community/Llama-3.2-1B-Instruct-ONNX': {
    minRAM: 4096, // MB
    minStorage: 1024, // MB
    requiresWebGPU: true,
    preferredCores: 4
  },
  'Xenova/LaMini-GPT-774M': {
    minRAM: 2048, // MB
    minStorage: 512, // MB
    requiresWebGPU: false,
    preferredCores: 2
  },
  'Xenova/gpt2': {
    minRAM: 1024, // MB
    minStorage: 256, // MB
    requiresWebGPU: false,
    preferredCores: 1
  },
  'Xenova/distilgpt2': {
    minRAM: 512, // MB
    minStorage: 128, // MB
    requiresWebGPU: false,
    preferredCores: 1
  }
} as const;

// Legacy server-side LLM check (for backward compatibility)
export function shouldUseClientLLM(): boolean {
  return LLM_CONFIG.INFERENCE_MODE === 'client';
}

export function shouldUseServerLLM(): boolean {
  return LLM_CONFIG.INFERENCE_MODE === 'server';
}

// Model utility functions
export function getModelType(modelName: string): 'instruct' | 'conversational' | 'unknown' {
  return SUPPORTED_MODELS[modelName as keyof typeof SUPPORTED_MODELS]?.type || 'unknown';
}

export function isModelSupported(modelName: string): boolean {
  return modelName in SUPPORTED_MODELS;
}

export function getModelInfo(modelName: string) {
  return SUPPORTED_MODELS[modelName as keyof typeof SUPPORTED_MODELS];
}

export function getModelRequirements(modelName: string) {
  return MODEL_REQUIREMENTS[modelName as keyof typeof MODEL_REQUIREMENTS];
}
