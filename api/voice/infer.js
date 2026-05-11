const DEFAULT_ALLOWED_ORIGINS = [
  'https://portland-laws.github.io',
  'https://211-ai.github.io',
  'http://localhost:5173',
  'http://127.0.0.1:5173',
];

const ROUTE_RULES = {
  infer: {
    description: 'Generic upstream infer passthrough. Supports whichever content types the upstream /infer endpoint accepts.',
  },
  tts: {
    expectedContentType: 'application/x-www-form-urlencoded',
    description: 'Text-to-speech style request. Send form-urlencoded fields such as text and voice_description.',
  },
  stt: {
    expectedContentType: 'multipart/form-data',
    description: 'Speech-to-text or audio inference style request. Send multipart form data with an audio field.',
  },
};

function parseAllowedOrigins() {
  return (process.env.VOICE_PROXY_ALLOWED_ORIGINS || process.env.OPENROUTER_PROXY_ALLOWED_ORIGINS || DEFAULT_ALLOWED_ORIGINS.join(','))
    .split(',')
    .map((origin) => origin.trim())
    .filter(Boolean);
}

function setCorsHeaders(req, res) {
  const origin = req.headers.origin || '';
  const allowedOrigins = parseAllowedOrigins();
  const allowedOrigin = allowedOrigins.includes(origin) ? origin : allowedOrigins[0];
  const requestedHeaders = req.headers['access-control-request-headers'];
  const allowHeaders = requestedHeaders || 'Content-Type';

  res.setHeader('Access-Control-Allow-Origin', allowedOrigin);
  res.setHeader('Vary', 'Origin');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', allowHeaders);
  res.setHeader('Access-Control-Max-Age', '86400');
}

function readRawBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let total = 0;

    req.on('data', (chunk) => {
      total += chunk.length;
      if (total > 50 * 1024 * 1024) {
        reject(new Error('Audio upload too large'));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

function getRouteIntent(req) {
  return req.voiceProxyRouteIntent || 'infer';
}

function matchesExpectedContentType(contentType, expectedContentType) {
  if (!contentType || !expectedContentType) {
    return true;
  }
  return contentType.toLowerCase().startsWith(expectedContentType.toLowerCase());
}

function buildRouteDiagnostic(req, contentType) {
  const routeIntent = getRouteIntent(req);
  const routeRule = ROUTE_RULES[routeIntent] || ROUTE_RULES.infer;
  return {
    route: routeIntent,
    requestContentType: contentType || null,
    expectedContentType: routeRule.expectedContentType || null,
    routeDescription: routeRule.description,
    upstream: process.env.VOICE_PROXY_UPSTREAM_URL || 'http://10.8.0.99:8000/infer',
  };
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

  const upstreamUrl = process.env.VOICE_PROXY_UPSTREAM_URL || 'http://10.8.0.99:8000/infer';
  const apiKey = process.env.VOICE_PROXY_API_KEY;
  const routeIntent = getRouteIntent(req);

  try {
    const body = await readRawBody(req);
    const contentType = req.headers['content-type'];

    if (!contentType) {
      res.status(400).json({ error: 'Content-Type is required' });
      return;
    }

    const routeRule = ROUTE_RULES[routeIntent] || ROUTE_RULES.infer;
    if (!matchesExpectedContentType(contentType, routeRule.expectedContentType)) {
      res.status(400).json({
        error: 'Request shape does not match route intent',
        message: `The /${routeIntent} route expects ${routeRule.expectedContentType}, but received ${contentType}.`,
        diagnostic: buildRouteDiagnostic(req, contentType),
      });
      return;
    }

    const upstreamHeaders = {
      'content-type': contentType,
    };
    if (apiKey) {
      upstreamHeaders['x-api-key'] = apiKey;
    }

    const upstream = await fetch(upstreamUrl, {
      method: 'POST',
      headers: upstreamHeaders,
      body,
    });

    const upstreamContentType = upstream.headers.get('content-type') || 'application/octet-stream';
    res.setHeader('X-Voice-Proxy-Route', routeIntent);
    res.setHeader('X-Voice-Proxy-Upstream', upstreamUrl);
    res.setHeader('X-Voice-Proxy-Upstream-Status', String(upstream.status));
    res.setHeader('X-Voice-Proxy-Upstream-Content-Type', upstreamContentType);

    if (!upstream.ok) {
      const upstreamBody = await upstream.text().catch(() => '');
      res.status(upstream.status).json({
        error: 'Voice upstream request failed',
        message: `Upstream returned ${upstream.status} for route ${routeIntent}.`,
        diagnostic: {
          ...buildRouteDiagnostic(req, contentType),
          upstreamStatus: upstream.status,
          upstreamContentType,
          upstreamBodyPreview: upstreamBody.slice(0, 1000),
        },
      });
      return;
    }

    res.status(upstream.status);
    res.setHeader('Content-Type', upstreamContentType);
    const disposition = upstream.headers.get('content-disposition');
    if (disposition) {
      res.setHeader('Content-Disposition', disposition);
    }
    res.send(Buffer.from(await upstream.arrayBuffer()));
  } catch (error) {
    res.status(500).json({
      error: 'Voice proxy failed',
      message: error instanceof Error ? error.message : String(error),
    });
  }
}