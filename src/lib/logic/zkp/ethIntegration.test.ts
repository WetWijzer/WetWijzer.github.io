import {
  ETH_INTEGRATION_METADATA,
  buildEthTransactionRequest,
  buildVerifierReadCall,
  callEth,
  chainIdToHex,
  normalizeEthAddress,
  sendEthTransaction,
} from './ethIntegration';

describe('EVM browser integration helpers', () => {
  const address = `0x${'ab'.repeat(20)}`;
  const sender = `${'cd'.repeat(20)}`;

  it('declares the eth_integration.py browser-native contract', () => {
    expect(ETH_INTEGRATION_METADATA).toEqual({
      pythonSource: 'logic/zkp/eth_integration.py',
      runtime: 'browser-native',
      requiresPythonRuntime: false,
      allowsServerRpcFallback: false,
      providerContract: 'eip1193-injected',
    });
  });

  it('normalizes values and builds transaction dictionaries', () => {
    expect(normalizeEthAddress(` ${address.toUpperCase()} `)).toBe(address);
    expect(chainIdToHex(11155111)).toBe('0xaa36a7');
    expect(chainIdToHex('0XAA36A7')).toBe('0xaa36a7');
    expect(
      buildEthTransactionRequest({
        to: address,
        data: 'AABB',
        from: sender,
        value: '15',
        chainId: 1,
      }),
    ).toEqual({
      to: address,
      data: '0xaabb',
      from: `0x${sender}`,
      value: '0xf',
      chainId: '0x1',
    });
  });

  it('builds verifier calls and delegates only to an injected provider', async () => {
    const calls: Array<{ method: string; params?: Array<unknown> }> = [];
    const provider = {
      request: async (args: { method: string; params?: Array<unknown> }): Promise<string> => {
        calls.push(args);
        return '0xresult';
      },
    };
    const tx = buildEthTransactionRequest({ to: address, data: 'abcd' });
    const read = buildVerifierReadCall({ verifierAddress: address, calldata: 'beef' });
    await expect(sendEthTransaction(provider, tx)).resolves.toBe('0xresult');
    await expect(callEth(provider, read)).resolves.toBe('0xresult');
    expect(calls).toEqual([
      { method: 'eth_sendTransaction', params: [tx] },
      { method: 'eth_call', params: [{ to: address, data: '0xbeef' }, 'latest'] },
    ]);
  });

  it('fails closed for malformed values and missing provider', async () => {
    expect(() => normalizeEthAddress('abc')).toThrow('20 bytes');
    expect(() => normalizeEthAddress(`0x${'zz'.repeat(20)}`)).toThrow('hex');
    expect(() => chainIdToHex(-1)).toThrow('non-negative');
    expect(() => buildEthTransactionRequest({ to: address, data: 'abc' })).toThrow(
      'even-length hex',
    );
    await expect(sendEthTransaction(undefined, { to: address, data: '0x' })).rejects.toThrow(
      'no server RPC fallback',
    );
    await expect(
      callEth(undefined, { to: address, data: '0x', blockTag: 'latest' }),
    ).rejects.toThrow('no server RPC fallback');
  });
});
