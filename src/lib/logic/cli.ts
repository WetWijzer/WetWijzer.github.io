import { createLogicApi, type LogicApiOptions } from './api';
import { validateBrowserNativeLogicRuntime } from './browserNativeValidation';
import type { BridgeProofRequest, LogicBridgeFormat } from './integration/bridge';

export type LogicCliCommand = 'health' | 'convert' | 'prove' | 'policy' | 'validate';
export interface LogicCliResult {
  ok: boolean;
  exitCode: 0 | 1 | 2;
  command?: LogicCliCommand;
  stdout: string;
  stderr: string;
  data?: Record<string, unknown>;
  runtime: Runtime;
}
export type LogicDevtoolsFlagValue = string | number | boolean | readonly string[];
export interface LogicDevtoolsCommandInvocation {
  command?: LogicCliCommand;
  argv?: readonly string[];
  flags?: Record<string, LogicDevtoolsFlagValue | undefined>;
}
export interface LogicDevtoolsCommandAdapter {
  readonly browserNative: true;
  readonly pythonRuntime: false;
  readonly serverRuntime: false;
  readonly commands: readonly LogicCliCommand[];
  run(invocation: LogicDevtoolsCommandInvocation): LogicCliResult;
}
type Runtime = {
  browserNative: true;
  pythonRuntime: false;
  serverRuntime: false;
  serverCallsAllowed: false;
};

const runtime: Runtime = {
  browserNative: true,
  pythonRuntime: false,
  serverRuntime: false,
  serverCallsAllowed: false,
};
const commands: readonly LogicCliCommand[] = ['health', 'convert', 'prove', 'policy', 'validate'];
const formats: readonly LogicBridgeFormat[] = [
  'natural_language',
  'legal_text',
  'fol',
  'deontic',
  'tdfol',
  'cec',
  'dcec',
  'prolog',
  'tptp',
  'json',
  'defeasible',
];
const blockedRuntime =
  /(?:^|\s)(?:python|python3|py|pip|uv|node|curl)\b|https?:\/\/|file:\/\/|subprocess|rpc:\/\//i;

export function runLogicCli(
  argv: readonly string[],
  options: LogicApiOptions = {},
): LogicCliResult {
  const args = [...argv];
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    return pass('health', `logic commands: ${commands.join(', ')}`, {
      commands: [...commands],
    });
  }
  if (blockedRuntime.test(args.join(' '))) {
    return fail(
      undefined,
      2,
      'Runtime fallbacks are not available for browser-native logic CLI commands.',
    );
  }

  const command = args.shift() as LogicCliCommand;
  const flags = parseFlags(args);
  const api = createLogicApi(options);
  if (command === 'health') {
    return pass(command, 'logic runtime: browser-native-typescript-wasm', {
      runtime: 'browser-native-typescript-wasm',
      ...runtime,
    });
  }
  if (command === 'convert') {
    const source = first(flags, 'source', 'text', 'input');
    if (source === undefined) {
      return fail(command, 2, 'convert requires --source <text>.');
    }
    const result = api.convertLogic(
      source,
      format(flags, 'from', 'source-format', 'source_format') ?? 'natural_language',
      format(flags, 'to', 'target-format', 'target_format') ?? 'fol',
    );
    const data: Record<string, unknown> = { ...result.toDict(), command, ...runtime };
    return result.status === 'failed' || result.status === 'unsupported'
      ? fail(command, 1, String(data.error ?? data.status), data)
      : pass(command, String(data.target_formula ?? data.targetFormula ?? ''), data);
  }
  if (command === 'prove') {
    const theorem = first(flags, 'theorem', 'goal');
    const axioms = values(flags, 'axiom', 'axioms');
    if (theorem === undefined || axioms.length === 0) {
      return fail(
        command,
        2,
        'prove requires --theorem <formula> and at least one --axiom <formula>.',
      );
    }
    const result = api.prove({ logic: proofLogic(flags) ?? 'cec', theorem, axioms });
    const data: Record<string, unknown> = { ...result, command, ...runtime };
    return result.status === 'error'
      ? fail(command, 1, result.error ?? 'proof failed', data)
      : pass(command, result.status, data);
  }
  if (command === 'policy') {
    const text = first(flags, 'source', 'text', 'input');
    if (text === undefined) {
      return fail(command, 2, 'policy requires --source <natural-language policy>.');
    }
    const result = api.compileNlToPolicy(text);
    const data: Record<string, unknown> = { ...result, command, ...runtime };
    return result.success
      ? pass(command, result.policyFormula, data)
      : fail(command, 1, result.warnings.join('; ') || 'policy compilation failed', data);
  }
  if (command === 'validate') {
    const data: Record<string, unknown> = {
      ...validateBrowserNativeLogicRuntime({
        folText: first(flags, 'fol-text', 'fol_text'),
        deonticText: first(flags, 'deontic-text', 'deontic_text'),
      }),
      command,
      ...runtime,
    };
    return data.valid === true
      ? pass(command, 'browser-native logic runtime valid', data)
      : fail(command, 1, 'browser-native logic runtime validation failed', data);
  }
  return fail(undefined, 2, `Unknown logic CLI command: ${String(command)}`);
}

export const run_logic_cli = runLogicCli;

export function createLogicDevtoolsCommandAdapter(
  options: LogicApiOptions = {},
): LogicDevtoolsCommandAdapter {
  return {
    browserNative: true,
    pythonRuntime: false,
    serverRuntime: false,
    commands,
    run(invocation: LogicDevtoolsCommandInvocation): LogicCliResult {
      return runLogicCli(toArgv(invocation), options);
    },
  };
}

export function runLogicDevtoolsCommand(
  invocation: LogicDevtoolsCommandInvocation,
  options: LogicApiOptions = {},
): LogicCliResult {
  return createLogicDevtoolsCommandAdapter(options).run(invocation);
}

export const create_logic_devtools_command_adapter = createLogicDevtoolsCommandAdapter;
export const run_logic_devtools_command = runLogicDevtoolsCommand;

function toArgv(invocation: LogicDevtoolsCommandInvocation): readonly string[] {
  if (invocation.argv !== undefined) {
    return [...invocation.argv];
  }
  const argv: Array<string> = [];
  if (invocation.command !== undefined) {
    argv.push(invocation.command);
  }
  const flags = invocation.flags ?? {};
  for (const [key, value] of Object.entries(flags)) {
    if (value === undefined || value === false) {
      continue;
    }
    const flagValues = Array.isArray(value) ? value : [String(value)];
    for (const item of flagValues) {
      argv.push(`--${key}`);
      if (item !== 'true') {
        argv.push(item);
      }
    }
  }
  return argv;
}

function parseFlags(args: readonly string[]): Map<string, Array<string>> {
  const flags = new Map<string, Array<string>>();
  for (let index = 0; index < args.length; index += 1) {
    const raw = args[index];
    if (!raw.startsWith('--')) {
      continue;
    }
    const next = args[index + 1];
    const value = next !== undefined && !next.startsWith('--') ? next : 'true';
    if (value !== 'true') {
      index += 1;
    }
    flags.set(raw.slice(2), [...(flags.get(raw.slice(2)) ?? []), value]);
  }
  return flags;
}

function first(flags: Map<string, Array<string>>, ...keys: readonly string[]): string | undefined {
  for (const key of keys) {
    const value = flags.get(key)?.[0];
    if (value !== undefined && value.trim().length > 0) {
      return value;
    }
  }
  return undefined;
}

function values(flags: Map<string, Array<string>>, ...keys: readonly string[]): string[] {
  return keys.flatMap((key) => flags.get(key) ?? []).filter((value) => value.trim().length > 0);
}

function format(
  flags: Map<string, Array<string>>,
  ...keys: readonly string[]
): LogicBridgeFormat | undefined {
  const value = first(flags, ...keys);
  return value !== undefined && formats.includes(value as LogicBridgeFormat)
    ? (value as LogicBridgeFormat)
    : undefined;
}

function proofLogic(flags: Map<string, Array<string>>): BridgeProofRequest['logic'] | undefined {
  const value = first(flags, 'logic');
  return value === 'tdfol' || value === 'cec' || value === 'dcec' ? value : undefined;
}

function pass(
  command: LogicCliCommand,
  stdout: string,
  data: Record<string, unknown>,
): LogicCliResult {
  return { ok: true, exitCode: 0, command, stdout, stderr: '', data, runtime };
}

function fail(
  command: LogicCliCommand | undefined,
  exitCode: 1 | 2,
  stderr: string,
  data?: Record<string, unknown>,
): LogicCliResult {
  return { ok: false, exitCode, command, stdout: '', stderr, data, runtime };
}
