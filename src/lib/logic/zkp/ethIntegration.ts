export interface Eip1193Provider {
  request(args: { method: string; params?: Array<unknown> }): Promise<unknown>;
}
export interface EthTxRequest {
  to: string;
  data: string;
  from?: string;
  value?: string;
  chainId?: string;
}
export interface EthReadCallRequest {
  to: string;
  data: string;
  blockTag: 'latest';
}
export const ETH_INTEGRATION_METADATA = {
  pythonSource: 'logic/zkp/eth_integration.py',
  runtime: 'browser-native',
  requiresPythonRuntime: false,
  allowsServerRpcFallback: false,
  providerContract: 'eip1193-injected',
} as const;
export function normalizeEthAddress(address: string): string {
  const hex = stripPrefix(checkedString(address, 'address').trim().toLowerCase());
  if (hex.length !== 40) {
    throw new Error('address must be 20 bytes (40 hex chars)');
  }
  if (!/^[0-9a-f]+$/.test(hex)) {
    throw new Error('address must be hex');
  }
  return `0x${hex}`;
}
export function normalize_eth_address(address: string): string {
  return normalizeEthAddress(address);
}
export function chainIdToHex(chainId: number | bigint | string): string {
  return quantityToHex(chainId, 'chain_id');
}
export function chain_id_to_hex(chainId: number | bigint | string): string {
  return chainIdToHex(chainId);
}
export function buildEthTransactionRequest(options: {
  to: string;
  data: string;
  from?: string;
  value?: number | bigint | string;
  chainId?: number | bigint | string;
}): EthTxRequest {
  return {
    to: normalizeEthAddress(options.to),
    data: normalizeHexData(options.data),
    ...(options.from === undefined ? {} : { from: normalizeEthAddress(options.from) }),
    ...(options.value === undefined ? {} : { value: quantityToHex(options.value, 'value') }),
    ...(options.chainId === undefined ? {} : { chainId: chainIdToHex(options.chainId) }),
  };
}
export function buildVerifierReadCall(options: {
  verifierAddress: string;
  calldata: string;
}): EthReadCallRequest {
  return {
    to: normalizeEthAddress(options.verifierAddress),
    data: normalizeHexData(options.calldata),
    blockTag: 'latest',
  };
}
export async function sendEthTransaction(
  provider: Eip1193Provider | undefined,
  request: EthTxRequest,
): Promise<unknown> {
  return requireProvider(provider).request({ method: 'eth_sendTransaction', params: [request] });
}
export async function callEth(
  provider: Eip1193Provider | undefined,
  request: EthReadCallRequest,
): Promise<unknown> {
  return requireProvider(provider).request({
    method: 'eth_call',
    params: [{ to: request.to, data: request.data }, request.blockTag],
  });
}
function normalizeHexData(data: string): string {
  const hex = stripPrefix(checkedString(data, 'data').trim().toLowerCase());
  if (hex === '') {
    return '0x';
  }
  if (!/^[0-9a-f]+$/.test(hex) || hex.length % 2 !== 0) {
    throw new Error('data must be even-length hex');
  }
  return `0x${hex}`;
}
function quantityToHex(value: number | bigint | string, field: string): string {
  if (typeof value === 'string') {
    const trimmed = value.trim().toLowerCase();
    if (trimmed.startsWith('0x')) {
      if (!/^0x[0-9a-f]+$/.test(trimmed)) {
        throw new Error(`${field} hex string must be hex`);
      }
      return trimmed;
    }
    if (!/^[0-9]+$/.test(trimmed)) {
      throw new Error(`${field} string must be decimal or 0x-prefixed hex`);
    }
    return `0x${BigInt(trimmed).toString(16)}`;
  }
  if (typeof value === 'number' && !Number.isInteger(value)) {
    throw new TypeError(`${field} must be int or str`);
  }
  const integer = BigInt(value);
  if (integer < BigInt(0)) {
    throw new Error(`${field} must be non-negative`);
  }
  return `0x${integer.toString(16)}`;
}
function requireProvider(provider: Eip1193Provider | undefined): Eip1193Provider {
  if (provider === undefined) {
    throw new Error('EIP-1193 provider is required; no server RPC fallback is available.');
  }
  return provider;
}
function stripPrefix(value: string): string {
  return value.startsWith('0x') ? value.slice(2) : value;
}
function checkedString(value: string, field: string): string {
  if (typeof value !== 'string') {
    throw new TypeError(`${field} must be a str`);
  }
  return value;
}
