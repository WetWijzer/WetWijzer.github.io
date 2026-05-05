import {
  build_groth16_backend_options_from_setup,
  load_groth16_setup_artifacts,
  prepareGroth16SetupArtifacts,
  setup_groth16_artifacts,
} from './index';

const verificationKey = {
  IC: ['1', '2'],
  protocol: 'groth16',
  vk_alpha_1: ['1', '2'],
  vk_beta_2: [['3', '4']],
  vk_delta_2: [['7', '8']],
  vk_gamma_2: [['5', '6']],
};

describe('Groth16 setup artifact helpers', () => {
  it('normalizes browser-provided setup artifacts', () => {
    const wasm = new Uint8Array([1, 2, 3]);
    const setup = prepareGroth16SetupArtifacts({
      circuit_id: 'legal_test',
      circuit_version: 2,
      ruleset_id: 'rules-v2',
      verification_key: verificationKey,
      wasm,
      zkey: 'zkey-bytes',
    });
    wasm[0] = 9;
    expect(setup.circuitId).toBe('legal_test');
    expect(setup.circuitVersion).toBe(2);
    expect(setup.rulesetId).toBe('rules-v2');
    expect(setup.metadata.source_python_module).toBe('logic/zkp/setup_artifacts.py');
    expect(setup.verificationKey).toEqual(verificationKey);
    expect(setup.provingArtifacts.zkey).toBe('zkey-bytes');
    expect(Array.from(setup.provingArtifacts.wasm as Uint8Array)).toEqual([1, 2, 3]);
  });

  it('accepts Python-style aliases and builds backend options', () => {
    const setup = setup_groth16_artifacts({
      circuit_wasm: 'wasm-bytes',
      proving_key: 'pk-bytes',
      verificationKey: JSON.stringify(verificationKey),
    });
    expect(setup.provingArtifacts).toEqual({ wasm: 'wasm-bytes', zkey: 'pk-bytes' });
    expect(setup.verificationKey).toEqual(verificationKey);
    expect(
      build_groth16_backend_options_from_setup({
        circuitId: 'circuit',
        circuitVersion: 3,
        rulesetId: 'rules',
        verificationKey,
        wasm: 'wasm',
        zkey: 'zkey',
      }),
    ).toMatchObject({ circuitId: 'circuit', circuitVersion: 3, rulesetId: 'rules' });
  });

  it('fails closed for invalid artifacts and filesystem paths', () => {
    expect(() => prepareGroth16SetupArtifacts({ zkey: 'zkey', verificationKey })).toThrow(
      'missing wasm/circuitWasm/circuit_wasm bytes',
    );
    expect(() =>
      prepareGroth16SetupArtifacts({
        verificationKey: { protocol: 'other' },
        wasm: 'w',
        zkey: 'z',
      }),
    ).toThrow('missing valid verification key');
    expect(() => load_groth16_setup_artifacts('./setup.json')).toThrow(
      'Filesystem setup artifact loading is not browser-native',
    );
  });
});
