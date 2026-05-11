#!/usr/bin/env node
import http from 'node:http';
import handler from '../api/voice/infer.js';

const port = Number(process.env.PORT || process.env.VOICE_PROXY_PORT || 8790);
const host = process.env.HOST || process.env.VOICE_PROXY_HOST || '127.0.0.1';

function parseAllowedOrigins() {
  return (process.env.VOICE_PROXY_ALLOWED_ORIGINS || process.env.OPENROUTER_PROXY_ALLOWED_ORIGINS || 'https://portland-laws.github.io,https://211-ai.github.io,http://localhost:5173,http://127.0.0.1:5173')
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

function createResponseAdapter(res) {
  return {
    statusCode: 200,
    setHeader: (...args) => res.setHeader(...args),
    status(code) {
      this.statusCode = code;
      res.statusCode = code;
      return this;
    },
    json(payload) {
      if (!res.hasHeader('Content-Type')) {
        res.setHeader('Content-Type', 'application/json; charset=utf-8');
      }
      res.end(JSON.stringify(payload));
    },
    send(payload) {
      res.end(payload);
    },
    end(payload) {
      res.end(payload);
    },
  };
}

const server = http.createServer(async (req, res) => {
  const pathname = new URL(req.url || '/', `http://${req.headers.host || 'localhost'}`).pathname;
  setCorsHeaders(req, res);

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  if (pathname === '/health' || pathname === '/api/voice/health') {
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({
      ok: true,
      service: 'voice-proxy',
      configured: true,
      requiresApiKey: Boolean(process.env.VOICE_PROXY_API_KEY),
      upstream: process.env.VOICE_PROXY_UPSTREAM_URL || 'http://10.8.0.99:8000/infer',
    }));
    return;
  }

  if (
    pathname !== '/api/voice/infer' &&
    pathname !== '/infer' &&
    pathname !== '/api/voice/tts' &&
    pathname !== '/tts' &&
    pathname !== '/api/voice/stt' &&
    pathname !== '/stt'
  ) {
    res.writeHead(404, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ error: 'Not found' }));
    return;
  }

  try {
    await handler(req, createResponseAdapter(res));
  } catch (error) {
    if (!res.headersSent) {
      res.writeHead(500, { 'Content-Type': 'application/json; charset=utf-8' });
    }
    res.end(JSON.stringify({
      error: 'Voice proxy crashed',
      message: error instanceof Error ? error.message : String(error),
    }));
  }
});

server.listen(port, host, () => {
  console.log(`Voice proxy listening on http://${host}:${port}`);
  console.log('Voice endpoint: /api/voice/infer');
  console.log('Voice aliases: /api/voice/tts, /api/voice/stt');
});