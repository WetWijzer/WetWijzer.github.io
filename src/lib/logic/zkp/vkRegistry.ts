import { parseCircuitRefLenient } from './statement';

const U64_MAX = (BigInt(1) << BigInt(64)) - BigInt(1);

export type VKHashInput = Uint8Array | string | Array<unknown> | Record<string, unknown>;

export interface VKRegistryEntry {
  circuitId: string;
  version: number | bigint;
  vkHashHex: string;
}

export interface VKRegistryDict {
  vk_registry: Record<string, Record<string, string>>;
}

export async function computeVkHash(vk: VKHashInput): Promise<string> {
  let payload: Uint8Array;
  if (vk instanceof Uint8Array) {
    payload = vk;
  } else if (typeof vk === 'string') {
    payload = new TextEncoder().encode(vk);
  } else if (Array.isArray(vk) || (vk && typeof vk === 'object')) {
    payload = new TextEncoder().encode(stableJsonStringify(vk));
  } else {
    throw new TypeError('vk must be bytes, str, dict, or list');
  }
  const digest = await globalThis.crypto.subtle.digest('SHA-256', payload);
  return bytesToHex(new Uint8Array(digest));
}

export async function compute_vk_hash(vk: VKHashInput): Promise<string> {
  return computeVkHash(vk);
}

export class VKRegistry {
  private readonly entries = new Map<string, string>();

  constructor(entries?: Iterable<VKRegistryEntry>) {
    if (entries) {
      for (const entry of entries) {
        this.register(entry.circuitId, entry.version, entry.vkHashHex);
      }
    }
  }

  register(
    circuitId: string,
    version: number | bigint,
    vkHashHex: string,
    options: { overwrite?: boolean } = {},
  ): void {
    const normalizedCircuitId = validateCircuitId(circuitId);
    const normalizedVersion = validateVersion(version);
    const normalizedHash = validateVkHashHex(vkHashHex);
    const key = registryKey(normalizedCircuitId, normalizedVersion);
    const existing = this.entries.get(key);
    if (existing !== undefined && !options.overwrite) {
      if (existing !== normalizedHash) {
        throw new Error('VK hash already registered for this circuit_id/version');
      }
      return;
    }
    this.entries.set(key, normalizedHash);
  }

  registerVk(
    circuitId: string,
    version: number | bigint,
    vkHashHex: string,
    overwrite = false,
  ): void {
    this.register(circuitId, version, vkHashHex, { overwrite });
  }

  register_vk(
    circuitId: string,
    version: number | bigint,
    vkHashHex: string,
    overwrite = false,
  ): void {
    this.registerVk(circuitId, version, vkHashHex, overwrite);
  }

  get(circuitId: string, version: number | bigint): string | undefined {
    return this.entries.get(registryKey(validateCircuitId(circuitId), validateVersion(version)));
  }

  getVkHash(circuitId: string, version: number | bigint): string {
    const hash = this.get(circuitId, version);
    if (hash === undefined) {
      throw new Error('VK hash not registered for this circuit_id/version');
    }
    return hash;
  }

  get_vk_hash(circuitId: string, version: number | bigint): string {
    return this.getVkHash(circuitId, version);
  }

  getByRef(circuitRef: string): string | undefined {
    const parsed = parseCircuitRefLenient(circuitRef);
    return this.entries.get(registryKey(parsed.circuitId, validateVersion(parsed.version)));
  }

  get_by_ref(circuitRef: string): string | undefined {
    return this.getByRef(circuitRef);
  }

  listVersions(circuitId: string): number[] {
    const normalizedCircuitId = validateCircuitId(circuitId);
    const versions: number[] = [];
    for (const key of this.entries.keys()) {
      const [entryCircuitId, version] = key.split('\u0000');
      if (entryCircuitId === normalizedCircuitId) {
        versions.push(Number(version));
      }
    }
    return versions.sort((left, right) => left - right);
  }

  list_versions(circuitId: string): number[] {
    return this.listVersions(circuitId);
  }

  listEntries(): VKRegistryEntry[] {
    return [...this.entries.entries()]
      .map(([key, vkHashHex]) => {
        const [circuitId, version] = key.split('\u0000');
        return { circuitId, version: parseStoredVersion(version), vkHashHex };
      })
      .sort((left, right) =>
        left.circuitId === right.circuitId
          ? compareVersions(BigInt(left.version), BigInt(right.version))
          : left.circuitId.localeCompare(right.circuitId),
      );
  }

  list_entries(): VKRegistryEntry[] {
    return this.listEntries();
  }

  toDict(): VKRegistryDict {
    const vkRegistry: Record<string, Record<string, string>> = {};
    for (const [key, vkHashHex] of this.entries.entries()) {
      const [circuitId, version] = key.split('\u0000');
      vkRegistry[circuitId] ??= {};
      vkRegistry[circuitId][version] = vkHashHex;
    }
    return { vk_registry: vkRegistry };
  }

  to_dict(): VKRegistryDict {
    return this.toDict();
  }

  static fromDict(data: unknown): VKRegistry {
    if (!data || typeof data !== 'object' || Array.isArray(data) || !('vk_registry' in data)) {
      throw new TypeError("data must be a dict containing 'vk_registry'");
    }
    const raw = (data as VKRegistryDict).vk_registry;
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
      throw new TypeError("'vk_registry' must be a dict");
    }

    const entries: VKRegistryEntry[] = [];
    for (const [circuitId, versions] of Object.entries(raw)) {
      if (!versions || typeof versions !== 'object' || Array.isArray(versions)) {
        throw new TypeError('vk_registry values must be dicts');
      }
      for (const [versionString, vkHashHex] of Object.entries(versions)) {
        if (!/^[0-9]+$/.test(versionString)) {
          throw new Error('version keys must be base-10 integer strings');
        }
        entries.push({ circuitId, version: BigInt(versionString), vkHashHex: String(vkHashHex) });
      }
    }
    return new VKRegistry(entries);
  }

  static from_dict(data: unknown): VKRegistry {
    return VKRegistry.fromDict(data);
  }
}

export function validateCircuitId(circuitId: unknown): string {
  if (typeof circuitId !== 'string') {
    throw new TypeError('circuit_id must be a str');
  }
  if (circuitId === '') {
    throw new Error('circuit_id cannot be empty');
  }
  if (circuitId.includes('@')) {
    throw new Error("circuit_id must not contain '@'");
  }
  return circuitId;
}

export function validateVersion(version: unknown): bigint {
  if (typeof version !== 'number' && typeof version !== 'bigint') {
    throw new TypeError('version must be an int');
  }
  if (typeof version === 'number' && !Number.isInteger(version)) {
    throw new TypeError('version must be an int');
  }
  if (typeof version === 'number' && !Number.isSafeInteger(version)) {
    throw new TypeError(
      'version must be a safe integer number; use bigint for uint64 values above Number.MAX_SAFE_INTEGER',
    );
  }
  const normalized = BigInt(version);
  if (normalized < BigInt(0) || normalized > U64_MAX) {
    throw new Error('version must be in uint64 range');
  }
  return normalized;
}

export function validateVkHashHex(vkHashHex: unknown): string {
  if (typeof vkHashHex !== 'string') {
    throw new TypeError('vk_hash_hex must be a str');
  }
  if (vkHashHex.length !== 64) {
    throw new Error('vk_hash_hex must be 64 hex characters');
  }
  if (!/^[0-9a-fA-F]+$/.test(vkHashHex)) {
    throw new Error('vk_hash_hex must be hex');
  }
  return vkHashHex.toLowerCase();
}

function registryKey(circuitId: string, version: bigint): string {
  return `${circuitId}\u0000${version.toString()}`;
}

function parseStoredVersion(version: string): number | bigint {
  const asBigInt = BigInt(version);
  return asBigInt <= BigInt(Number.MAX_SAFE_INTEGER) ? Number(asBigInt) : asBigInt;
}

function compareVersions(left: bigint, right: bigint): number {
  if (left < right) {
    return -1;
  }
  if (left > right) {
    return 1;
  }
  return 0;
}

function stableJsonStringify(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map(stableJsonStringify).join(',')}]`;
  }
  if (value && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableJsonStringify(record[key])}`)
      .join(',')}}`;
  }
  if (typeof value === 'number' && !Number.isFinite(value)) {
    throw new TypeError('vk JSON values must be finite');
  }
  if (
    typeof value === 'bigint' ||
    typeof value === 'undefined' ||
    typeof value === 'function' ||
    typeof value === 'symbol'
  ) {
    throw new TypeError('vk must contain JSON-serializable values');
  }
  return JSON.stringify(value);
}

function bytesToHex(bytes: Uint8Array): string {
  return [...bytes].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}
