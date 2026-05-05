import { createHash, webcrypto } from 'node:crypto';
import { TextEncoder } from 'node:util';

import { VKRegistry, computeVkHash, compute_vk_hash } from './vkRegistry';

Object.defineProperty(globalThis, 'crypto', {
  value: webcrypto,
  configurable: true,
});
Object.defineProperty(globalThis, 'TextEncoder', {
  value: TextEncoder,
  configurable: true,
});

describe('VK registry browser-native parity', () => {
  it('computes stable VK hashes for bytes, text, and structured data', async () => {
    await expect(computeVkHash(new Uint8Array([1, 2, 3]))).resolves.toBe(
      createHash('sha256')
        .update(Buffer.from([1, 2, 3]))
        .digest('hex'),
    );
    await expect(computeVkHash('vk')).resolves.toBe(
      createHash('sha256').update('vk', 'utf8').digest('hex'),
    );
    await expect(computeVkHash({ b: 2, a: [1] })).resolves.toBe(
      createHash('sha256').update('{"a":[1],"b":2}', 'utf8').digest('hex'),
    );
    await expect(compute_vk_hash(['vk', null, true])).resolves.toBe(
      createHash('sha256').update('["vk",null,true]', 'utf8').digest('hex'),
    );
    await expect(computeVkHash(1 as never)).rejects.toThrow('vk must be bytes, str, dict, or list');
    await expect(computeVkHash({ a: undefined } as never)).rejects.toThrow('JSON-serializable');
    await expect(computeVkHash([Number.POSITIVE_INFINITY] as never)).rejects.toThrow('finite');
  });

  it('registers, looks up, serializes, and restores VK hashes', async () => {
    const hash = await computeVkHash('vk');
    const registry = new VKRegistry();

    registry.register('tdfol_v1', 1, hash.toUpperCase());
    registry.register('tdfol_v1', 1, hash);
    registry.register_vk('tdfol_v1', 2, hash, true);

    expect(registry.get('tdfol_v1', 1)).toBe(hash);
    expect(registry.get_vk_hash('tdfol_v1', 1)).toBe(hash);
    expect(registry.getByRef('tdfol_v1@v2')).toBe(hash);
    expect(registry.listVersions('tdfol_v1')).toEqual([1, 2]);
    expect(registry.list_entries()).toEqual([
      { circuitId: 'tdfol_v1', version: 1, vkHashHex: hash },
      { circuitId: 'tdfol_v1', version: 2, vkHashHex: hash },
    ]);
    expect(VKRegistry.fromDict(registry.toDict()).toDict()).toEqual(registry.toDict());
  });

  it('preserves uint64 versions above the safe number range with bigint callers', async () => {
    const hash = await computeVkHash('vk');
    const registry = new VKRegistry();
    const largeVersion = BigInt(Number.MAX_SAFE_INTEGER) + BigInt(2);

    registry.registerVk('tdfol_v1', largeVersion, hash);

    expect(registry.getVkHash('tdfol_v1', largeVersion)).toBe(hash);
    expect(registry.list_entries()).toEqual([
      { circuitId: 'tdfol_v1', version: largeVersion, vkHashHex: hash },
    ]);
    expect(VKRegistry.fromDict(registry.toDict()).getVkHash('tdfol_v1', largeVersion)).toBe(hash);
    expect(() => registry.registerVk('tdfol_v1', Number.MAX_SAFE_INTEGER + 2, hash)).toThrow(
      'safe integer',
    );
  });

  it('rejects invalid registry entries like the Python helper', async () => {
    const hash = await computeVkHash('vk');
    const registry = new VKRegistry();

    expect(() => registry.register('', 1, hash)).toThrow('circuit_id cannot be empty');
    expect(() => registry.register('bad@id', 1, hash)).toThrow("circuit_id must not contain '@'");
    expect(() => registry.register('tdfol_v1', -1, hash)).toThrow('uint64');
    expect(() => registry.register('tdfol_v1', 1, '00')).toThrow('64 hex');
    expect(() => registry.getVkHash('tdfol_v1', 99)).toThrow('not registered');
    registry.register('tdfol_v1', 1, hash);
    expect(() => registry.register('tdfol_v1', 1, '11'.repeat(32))).toThrow('already registered');
    expect(() => VKRegistry.fromDict({ vk_registry: { x: [] } })).toThrow(
      'vk_registry values must be dicts',
    );
    expect(() => VKRegistry.fromDict({ vk_registry: { x: { nope: hash } } })).toThrow(
      'version keys',
    );
  });
});
