const U64_MAX = (BigInt(1) << BigInt(64)) - BigInt(1);
const UINT64_MASK = (BigInt(1) << BigInt(64)) - BigInt(1);
const KECCAK_RATE_BYTES = 136;
const KECCAK_ROUND_CONSTANTS = [
  '0x0000000000000001',
  '0x0000000000008082',
  '0x800000000000808a',
  '0x8000000080008000',
  '0x000000000000808b',
  '0x0000000080000001',
  '0x8000000080008081',
  '0x8000000000008009',
  '0x000000000000008a',
  '0x0000000000000088',
  '0x0000000080008009',
  '0x000000008000000a',
  '0x000000008000808b',
  '0x800000000000008b',
  '0x8000000000008089',
  '0x8000000000008003',
  '0x8000000000008002',
  '0x8000000000000080',
  '0x000000000000800a',
  '0x800000008000000a',
  '0x8000000080008081',
  '0x8000000000008080',
  '0x0000000080000001',
  '0x8000000080008008',
].map((value) => BigInt(value));
const KECCAK_ROTATION_OFFSETS = [
  [0, 36, 3, 41, 18],
  [1, 44, 10, 45, 2],
  [62, 6, 43, 15, 61],
  [28, 55, 25, 21, 56],
  [27, 20, 39, 8, 14],
];

function rotl64(value: bigint, shift: number): bigint {
  const normalizedShift = shift % 64;
  if (normalizedShift === 0) {
    return value & UINT64_MASK;
  }
  return (
    ((value << BigInt(normalizedShift)) | (value >> BigInt(64 - normalizedShift))) & UINT64_MASK
  );
}

function keccakF1600(state: Array<bigint>): void {
  for (const roundConstant of KECCAK_ROUND_CONSTANTS) {
    const c = new Array<bigint>(5);
    const d = new Array<bigint>(5);
    for (let x = 0; x < 5; x += 1) {
      c[x] = state[x] ^ state[x + 5] ^ state[x + 10] ^ state[x + 15] ^ state[x + 20];
    }
    for (let x = 0; x < 5; x += 1) {
      d[x] = c[(x + 4) % 5] ^ rotl64(c[(x + 1) % 5], 1);
    }
    for (let x = 0; x < 5; x += 1) {
      for (let y = 0; y < 5; y += 1) {
        state[x + 5 * y] = (state[x + 5 * y] ^ d[x]) & UINT64_MASK;
      }
    }

    const b = new Array<bigint>(25).fill(BigInt(0));
    for (let x = 0; x < 5; x += 1) {
      for (let y = 0; y < 5; y += 1) {
        b[y + 5 * ((2 * x + 3 * y) % 5)] = rotl64(state[x + 5 * y], KECCAK_ROTATION_OFFSETS[x][y]);
      }
    }
    for (let x = 0; x < 5; x += 1) {
      for (let y = 0; y < 5; y += 1) {
        state[x + 5 * y] =
          (b[x + 5 * y] ^ (~b[((x + 1) % 5) + 5 * y] & b[((x + 2) % 5) + 5 * y])) & UINT64_MASK;
      }
    }
    state[0] = (state[0] ^ roundConstant) & UINT64_MASK;
  }
}

function utf8Bytes(value: string): Uint8Array {
  if (typeof TextEncoder !== 'undefined') {
    return new TextEncoder().encode(value);
  }
  const encoded = unescape(encodeURIComponent(value));
  const bytes = new Uint8Array(encoded.length);
  for (let index = 0; index < encoded.length; index += 1) {
    bytes[index] = encoded.charCodeAt(index);
  }
  return bytes;
}

export function keccak256Hex(value: string | Uint8Array): string {
  const input = typeof value === 'string' ? utf8Bytes(value) : value;
  const state = new Array<bigint>(25).fill(BigInt(0));
  for (let offset = 0; offset < input.length; offset += KECCAK_RATE_BYTES) {
    const block = input.slice(offset, Math.min(offset + KECCAK_RATE_BYTES, input.length));
    for (let index = 0; index < block.length; index += 1) {
      const lane = Math.floor(index / 8);
      state[lane] ^= BigInt(block[index]) << BigInt(8 * (index % 8));
    }
    if (block.length === KECCAK_RATE_BYTES) {
      keccakF1600(state);
    } else {
      const padLane = Math.floor(block.length / 8);
      state[padLane] ^= BigInt(1) << BigInt(8 * (block.length % 8));
      state[Math.floor((KECCAK_RATE_BYTES - 1) / 8)] ^=
        BigInt(128) << BigInt(8 * ((KECCAK_RATE_BYTES - 1) % 8));
      keccakF1600(state);
    }
  }
  if (input.length % KECCAK_RATE_BYTES === 0) {
    state[0] ^= BigInt(1);
    state[Math.floor((KECCAK_RATE_BYTES - 1) / 8)] ^=
      BigInt(128) << BigInt(8 * ((KECCAK_RATE_BYTES - 1) % 8));
    keccakF1600(state);
  }
  const output = new Array<string>();
  for (let index = 0; index < 32; index += 1) {
    const byte = Number((state[Math.floor(index / 8)] >> BigInt(8 * (index % 8))) & BigInt(255));
    output.push(byte.toString(16).padStart(2, '0'));
  }
  return `0x${output.join('')}`;
}

export interface RegisterVKPayload {
  circuitIdBytes32: string;
  version: number | bigint;
  vkHashBytes32: string;
}

export interface RegisterVKPayloadDict {
  circuit_id_bytes32: string;
  version: number | bigint;
  vk_hash_bytes32: string;
}

export function normalizeHexNoPrefix(value: string): string {
  if (typeof value !== 'string') {
    throw new TypeError('value must be a str');
  }
  const normalized = value.trim().toLowerCase();
  return normalized.startsWith('0x') ? normalized.slice(2) : normalized;
}

export function normalizeBytes32Hex(value: string): string {
  const normalized = normalizeHexNoPrefix(value);
  if (normalized.length !== 64) {
    throw new Error('value must be 32 bytes (64 hex chars)');
  }
  if (!/^[0-9a-f]+$/.test(normalized)) {
    throw new Error('value must be hex');
  }
  return `0x${normalized}`;
}

export function normalize_bytes32_hex(value: string): string {
  return normalizeBytes32Hex(value);
}

export function vkHashHexToBytes32(vkHashHex: string): string {
  return normalizeBytes32Hex(vkHashHex);
}

export function vk_hash_hex_to_bytes32(vkHashHex: string): string {
  return vkHashHexToBytes32(vkHashHex);
}

export function circuitIdTextToBytes32(_circuitIdText: string): string {
  if (typeof _circuitIdText !== 'string') {
    throw new TypeError('circuit_id_text must be a str');
  }
  if (_circuitIdText === '') {
    throw new Error('circuit_id_text cannot be empty');
  }
  return keccak256Hex(_circuitIdText);
}

export function circuit_id_text_to_bytes32(circuitIdText: string): string {
  return circuitIdTextToBytes32(circuitIdText);
}

export function buildRegisterVkPayload(options: {
  circuitIdBytes32: string;
  version: number | bigint;
  vkHashHex: string;
}): RegisterVKPayload {
  if (typeof options.version !== 'number' && typeof options.version !== 'bigint') {
    throw new TypeError('version must be int');
  }
  if (typeof options.version === 'number' && !Number.isInteger(options.version)) {
    throw new TypeError('version must be int');
  }
  const version = BigInt(options.version);
  if (version < BigInt(0) || version > U64_MAX) {
    throw new Error('version must fit uint64');
  }
  return {
    circuitIdBytes32: normalizeBytes32Hex(options.circuitIdBytes32),
    version: options.version,
    vkHashBytes32: vkHashHexToBytes32(options.vkHashHex),
  };
}

export function build_register_vk_payload(options: {
  circuit_id_bytes32: string;
  version: number | bigint;
  vk_hash_hex: string;
}): RegisterVKPayloadDict {
  const payload = buildRegisterVkPayload({
    circuitIdBytes32: options.circuit_id_bytes32,
    version: options.version,
    vkHashHex: options.vk_hash_hex,
  });
  return {
    circuit_id_bytes32: payload.circuitIdBytes32,
    version: payload.version,
    vk_hash_bytes32: payload.vkHashBytes32,
  };
}

function uint256Word(value: number | bigint): string {
  const version = BigInt(value);
  return version.toString(16).padStart(64, '0');
}

function boolWord(value: boolean): string {
  return value ? '1'.padStart(64, '0') : ''.padStart(64, '0');
}

export function buildRegisterVkCalldata(_options: {
  payload: RegisterVKPayload;
  overwrite?: boolean;
}): string {
  if (_options.overwrite !== undefined && typeof _options.overwrite !== 'boolean') {
    throw new TypeError('overwrite must be bool');
  }
  const payload = buildRegisterVkPayload({
    circuitIdBytes32: _options.payload.circuitIdBytes32,
    version: _options.payload.version,
    vkHashHex: _options.payload.vkHashBytes32,
  });
  const selector = keccak256Hex('registerVK(bytes32,uint64,bytes32,bool)').slice(2, 10);
  return [
    '0x',
    selector,
    payload.circuitIdBytes32.slice(2),
    uint256Word(payload.version),
    payload.vkHashBytes32.slice(2),
    boolWord(_options.overwrite ?? false),
  ].join('');
}

export function build_register_vk_calldata(options: {
  payload: RegisterVKPayloadDict;
  overwrite?: boolean;
}): string {
  return buildRegisterVkCalldata({
    overwrite: options.overwrite,
    payload: {
      circuitIdBytes32: options.payload.circuit_id_bytes32,
      version: options.payload.version,
      vkHashBytes32: options.payload.vk_hash_bytes32,
    },
  });
}
