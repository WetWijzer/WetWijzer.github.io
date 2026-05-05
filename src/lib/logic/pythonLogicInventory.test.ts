import { reconcilePythonLogicInventory } from './pythonLogicInventory';

describe('reconcilePythonLogicInventory', () => {
  it('captures the selected 269-to-253 inventory reconciliation', () => {
    const reconciliation = reconcilePythonLogicInventory();

    expect(reconciliation).toMatchObject({
      pythonInventoryFiles: 269,
      typescriptWasmImplementationFiles: 253,
      uncoveredPythonFiles: 16,
      browserNative: true,
      serverCallsAllowed: false,
      pythonRuntimeAllowed: false,
    });
    expect(reconciliation.tasks).toHaveLength(6);
    expect(reconciliation.tasks.reduce((total, task) => total + task.uncoveredFiles, 0)).toBe(16);
  });

  it('keeps uncovered behavior tasks browser-native and fail-closed', () => {
    const reconciliation = reconcilePythonLogicInventory();

    for (const task of reconciliation.tasks) {
      expect(task.task).toMatch(/TypeScript|WASM|browser|local/);
      expect(task.browserNative).toBe(true);
      expect(task.serverCallsAllowed).toBe(false);
      expect(task.pythonRuntimeAllowed).toBe(false);
    }
  });
});
