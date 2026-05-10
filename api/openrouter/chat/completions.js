const OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions';
const ALLOWED_MODELS = new Set([
  'liquid/lfm-2.5-1.2b-instruct:free',
  'liquid/lfm-2.5-1.2b-thinking:free',
]);

function parseAllowedOrigins() {
  return (process.env.OPENROUTER_PROXY_ALLOWED_ORIGINS || 'https://portland-laws.github.io,http://localhost:5173,http://127.0.0.1:5173')
    .split(',')
    .map((origin) => origin.trim())
    .filter(Boolean);
}

function setCorsHeaders(req, res) {
  const origin = req.headers.origin || '';
  const allowedOrigins = parseAllowedOrigins();
  const allowedOrigin = allowedOrigins.includes(origin) ? origin : allowedOrigins[0];
  const requestedHeaders = req.headers['access-control-request-headers'];
  const allowHeaders = requestedHeaders || 'Content-Type, Authorization, HTTP-Referer, X-OpenRouter-Title';

  res.setHeader('Access-Control-Allow-Origin', allowedOrigin);
  res.setHeader('Vary', 'Origin');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', allowHeaders);
  res.setHeader('Access-Control-Max-Age', '86400');
}

function readJsonBody(req) {
  if (req.body && typeof req.body === 'object') {
    return Promise.resolve(req.body);
  }

  return new Promise((resolve, reject) => {
    let raw = '';
    req.on('data', (chunk) => {
      raw += chunk;
      if (raw.length > 256_000) {
        reject(new Error('Request body too large'));
        req.destroy();
      }
    });
    req.on('end', () => {
      try {
        resolve(raw ? JSON.parse(raw) : {});
      } catch (error) {
        reject(error);
      }
    });
    req.on('error', reject);
  });
}

export default async function handler(req, res) {
  setCorsHeaders(req, res);

  if (req.method === 'OPTIONS') {
    res.status(204).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) {
    res.status(500).json({ error: 'OPENROUTER_API_KEY is not configured' });
    return;
  }

  try {
    const body = await readJsonBody(req);
    const model = body.model || 'liquid/lfm-2.5-1.2b-instruct:free';
    if (!ALLOWED_MODELS.has(model)) {
      res.status(400).json({ error: `Model ${model} is not allowed by this proxy` });
      return;
    }

    const upstream = await fetch(OPENROUTER_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
        'HTTP-Referer': process.env.OPENROUTER_SITE_URL || 'https://portland-laws.github.io',
        'X-OpenRouter-Title': process.env.OPENROUTER_SITE_NAME || 'Portland Laws',
      },
      body: JSON.stringify({
        ...body,
        model,
      }),
    });

    const contentType = upstream.headers.get('content-type') || 'application/json';
    res.status(upstream.status);
    res.setHeader('Content-Type', contentType);
    res.send(await upstream.text());
  } catch (error) {
    res.status(500).json({
      error: 'OpenRouter proxy failed',
      message: error instanceof Error ? error.message : String(error),
    });
  }
}
