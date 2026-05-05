export type PythonSurfaceKind = 'api' | 'cli';

export type BrowserNativeReplacementKind = 'typescript-developer-script' | 'browser-devtools';

export interface PythonSurfaceReplacement {
  readonly pythonSurface: string;
  readonly surfaceKind: PythonSurfaceKind;
  readonly replacementKind: BrowserNativeReplacementKind;
  readonly replacementName: string;
  readonly browserNative: true;
  readonly usesPythonRuntime: false;
  readonly usesServerRuntime: false;
  readonly notes: readonly string[];
}

export interface PythonSurfaceReplacementPlan {
  readonly replacements: readonly PythonSurfaceReplacement[];
  readonly rejectedSurfaces: readonly string[];
  readonly browserNative: true;
  readonly usesPythonRuntime: false;
  readonly usesServerRuntime: false;
}

export interface PythonLogicPublicApiSurface {
  readonly pythonModule: string;
  readonly publicApis: readonly string[];
}

export interface TypeScriptLogicPublicExportSurface {
  readonly typescriptModule: string;
  readonly publicExports: readonly string[];
}

export interface LogicPublicApiCompatibilityAdapter {
  readonly pythonApi: string;
  readonly typescriptExport: string;
  readonly adapterKind: 'direct-export' | 'snake-case-alias';
  readonly browserNative: true;
  readonly usesPythonRuntime: false;
  readonly usesServerRuntime: false;
}

export interface LogicPublicApiComparison {
  readonly pythonModule: string;
  readonly typescriptModule: string;
  readonly adapters: readonly LogicPublicApiCompatibilityAdapter[];
  readonly missingPythonApis: readonly string[];
  readonly coverageRatio: number;
  readonly browserNative: true;
  readonly usesPythonRuntime: false;
  readonly usesServerRuntime: false;
}

export interface LogicPublicApiCompatibilityReport {
  readonly comparisons: readonly LogicPublicApiComparison[];
  readonly adapters: readonly LogicPublicApiCompatibilityAdapter[];
  readonly missingPythonApis: readonly string[];
  readonly browserNative: true;
  readonly usesPythonRuntime: false;
  readonly usesServerRuntime: false;
}

const PYTHON_RUNTIME_MARKERS = [
  'python ',
  'python3 ',
  'py ',
  'pip ',
  'uv run python',
  'subprocess',
  'rpc://',
  'http://localhost',
  'https://localhost',
  'file://',
  '.py',
];

const DEFAULT_REPLACEMENTS: readonly PythonSurfaceReplacement[] = [
  {
    pythonSurface: 'ipfs_datasets_py.logic_api',
    surfaceKind: 'api',
    replacementKind: 'typescript-developer-script',
    replacementName: 'logic TypeScript module imports',
    browserNative: true,
    usesPythonRuntime: false,
    usesServerRuntime: false,
    notes: [
      'Import deterministic logic modules directly from src/lib/logic.',
      'Keep validation data serializable so browser tests and devtools can inspect it without filesystem access.',
    ],
  },
  {
    pythonSurface: 'ipfs_datasets_py.cli',
    surfaceKind: 'cli',
    replacementKind: 'browser-devtools',
    replacementName: 'browser console diagnostics',
    browserNative: true,
    usesPythonRuntime: false,
    usesServerRuntime: false,
    notes: [
      'Expose deterministic conversion and validation helpers through browser-loaded TypeScript modules.',
      'Do not shell out, open local files, or proxy to a Python process from browser runtime code.',
    ],
  },
  {
    pythonSurface: 'python -m ipfs_datasets_py',
    surfaceKind: 'cli',
    replacementKind: 'browser-devtools',
    replacementName: 'browser console diagnostics',
    browserNative: true,
    usesPythonRuntime: false,
    usesServerRuntime: false,
    notes: [
      'Treat Python module execution as a legacy CLI surface only.',
      'Use browser-native TypeScript diagnostics instead of spawning Python.',
    ],
  },
];

const DEFAULT_PYTHON_PUBLIC_APIS: readonly PythonLogicPublicApiSurface[] = [
  {
    pythonModule: 'logic/api.py',
    publicApis: [
      'convert_text_to_fol',
      'convert_legal_text_to_deontic',
      'convert_logic',
      'prove_logic',
      'create_logic_api',
      'get_global_logic_api',
      'reset_global_logic_api',
      'compile_nl_to_policy',
      'evaluate_nl_policy',
      'build_signed_delegation',
      'handle_logic_api_server_request',
    ],
  },
  { pythonModule: 'logic/cli.py', publicApis: ['run_logic_cli'] },
  {
    pythonModule: 'logic/ml_confidence.py',
    publicApis: ['extract_ml_confidence_features', 'predict_ml_confidence'],
  },
];

const DEFAULT_TYPESCRIPT_PUBLIC_EXPORTS: readonly TypeScriptLogicPublicExportSurface[] = [
  {
    typescriptModule: 'src/lib/logic/index.ts',
    publicExports: [
      'build_signed_delegation',
      'buildSignedDelegation',
      'compile_nl_to_policy',
      'compileNlToPolicy',
      'convert_legal_text_to_deontic',
      'convert_logic',
      'convert_text_to_fol',
      'convertLogic',
      'convertTextToFol',
      'createLogicApi',
      'create_logic_api',
      'evaluate_nl_policy',
      'evaluateNlPolicy',
      'getGlobalLogicApi',
      'get_global_logic_api',
      'handle_logic_api_server_request',
      'handleLogicApiServerRequest',
      'proveLogic',
      'prove_logic',
      'resetGlobalLogicApi',
      'reset_global_logic_api',
      'run_logic_cli',
    ],
  },
  {
    typescriptModule: 'src/lib/logic/mlConfidence.ts',
    publicExports: [
      'extract_ml_confidence_features',
      'extractConfidenceFeatures',
      'extractMLConfidenceFeatures',
      'predict_ml_confidence',
      'predictMLConfidence',
    ],
  },
];

function normalizeSurface(surface: string): string {
  return surface.trim().replace(/\s+/g, ' ');
}

function containsRuntimeFallback(surface: string): boolean {
  const normalized = normalizeSurface(surface).toLowerCase();
  return PYTHON_RUNTIME_MARKERS.some((marker) => normalized.includes(marker));
}

function snakeToCamel(name: string): string {
  return name.replace(/_([a-z0-9])/g, (_match, letter: string) => letter.toUpperCase());
}

function findTypeScriptExport(
  pythonApi: string,
  publicExports: ReadonlySet<string>,
):
  | {
      readonly typescriptExport: string;
      readonly adapterKind: 'direct-export' | 'snake-case-alias';
    }
  | undefined {
  if (publicExports.has(pythonApi)) {
    return { typescriptExport: pythonApi, adapterKind: 'direct-export' };
  }

  const camelCaseName = snakeToCamel(pythonApi);
  if (publicExports.has(camelCaseName)) {
    return { typescriptExport: camelCaseName, adapterKind: 'snake-case-alias' };
  }

  return undefined;
}

function inferReplacement(surface: string): PythonSurfaceReplacement | undefined {
  const normalized = normalizeSurface(surface);
  const exact = DEFAULT_REPLACEMENTS.find(
    (replacement) => replacement.pythonSurface === normalized,
  );

  if (exact) {
    return exact;
  }

  if (normalized.startsWith('ipfs_datasets_py.') && !containsRuntimeFallback(normalized)) {
    return {
      pythonSurface: normalized,
      surfaceKind: 'api',
      replacementKind: 'typescript-developer-script',
      replacementName: 'logic TypeScript module imports',
      browserNative: true,
      usesPythonRuntime: false,
      usesServerRuntime: false,
      notes: [
        'Port this Python API surface as deterministic TypeScript before exposing it to browser callers.',
        'Reject adapters that require Python, subprocesses, local files, RPC, or server endpoints.',
      ],
    };
  }

  return undefined;
}

export function createPythonSurfaceReplacementPlan(
  surfaces: readonly string[],
): PythonSurfaceReplacementPlan {
  const replacements: PythonSurfaceReplacement[] = [];
  const rejectedSurfaces: string[] = [];
  const seen = new Set<string>();

  for (const surface of surfaces) {
    const normalized = normalizeSurface(surface);
    if (normalized.length === 0 || seen.has(normalized)) {
      continue;
    }

    seen.add(normalized);
    const replacement = inferReplacement(normalized);

    if (replacement && !containsRuntimeFallback(replacement.replacementName)) {
      replacements.push(replacement);
    } else {
      rejectedSurfaces.push(normalized);
    }
  }

  return {
    replacements,
    rejectedSurfaces,
    browserNative: true,
    usesPythonRuntime: false,
    usesServerRuntime: false,
  };
}

export function compareLogicPublicApis(
  pythonApis: readonly PythonLogicPublicApiSurface[] = DEFAULT_PYTHON_PUBLIC_APIS,
  typescriptExports: readonly TypeScriptLogicPublicExportSurface[] = DEFAULT_TYPESCRIPT_PUBLIC_EXPORTS,
): LogicPublicApiCompatibilityReport {
  const comparisons: LogicPublicApiComparison[] = [];
  const allAdapters: LogicPublicApiCompatibilityAdapter[] = [];
  const allMissingPythonApis: string[] = [];

  for (const pythonSurface of pythonApis) {
    const typescriptSurface =
      typescriptExports.find((surface) =>
        pythonSurface.publicApis.some((api) => surface.publicExports.includes(api)),
      ) ?? typescriptExports[0];
    const publicExports = new Set<string>(typescriptSurface.publicExports);
    const adapters: LogicPublicApiCompatibilityAdapter[] = [];
    const missingPythonApis: string[] = [];

    for (const pythonApi of pythonSurface.publicApis) {
      const match = findTypeScriptExport(pythonApi, publicExports);
      if (match) {
        adapters.push({
          pythonApi,
          typescriptExport: match.typescriptExport,
          adapterKind: match.adapterKind,
          browserNative: true,
          usesPythonRuntime: false,
          usesServerRuntime: false,
        });
      } else {
        missingPythonApis.push(`${pythonSurface.pythonModule}:${pythonApi}`);
      }
    }

    allAdapters.push(...adapters);
    allMissingPythonApis.push(...missingPythonApis);
    comparisons.push({
      pythonModule: pythonSurface.pythonModule,
      typescriptModule: typescriptSurface.typescriptModule,
      adapters,
      missingPythonApis,
      coverageRatio:
        pythonSurface.publicApis.length === 0
          ? 1
          : adapters.length / pythonSurface.publicApis.length,
      browserNative: true,
      usesPythonRuntime: false,
      usesServerRuntime: false,
    });
  }

  return {
    comparisons,
    adapters: allAdapters,
    missingPythonApis: allMissingPythonApis,
    browserNative: true,
    usesPythonRuntime: false,
    usesServerRuntime: false,
  };
}
