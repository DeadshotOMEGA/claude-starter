/**
 * Document types supported by pdocs
 */
export type DocType =
  | 'plan'
  | 'investigation'
  | 'requirements'
  | 'feature-spec'
  | 'api-contract'
  | 'user-story'
  | 'user-flow'
  | 'agent'
  | 'skill'
  | 'claudemd'
  | 'rule'
  | 'command'
  | 'readme'
  | 'changelog';

/**
 * Document status in the registry
 */
export type DocStatus = 'valid' | 'invalid' | 'pending' | 'unregistered';

/**
 * Registry document entry
 */
export interface RegistryDocument {
  type: DocType;
  skill?: string;
  registered: string;
  lastValidated?: string;
  status: DocStatus;
}

/**
 * ID sequence tracking
 */
export interface IdSequences {
  [key: string]: number;
}

/**
 * Registry stats
 */
export interface RegistryStats {
  total: number;
  valid: number;
  invalid: number;
  pending: number;
}

/**
 * Full registry structure
 */
export interface Registry {
  version: string;
  updated: string;
  documents: Record<string, RegistryDocument>;
  id_sequences: IdSequences;
  stats: RegistryStats;
}

/**
 * Skill manifest structure
 */
export interface SkillManifest {
  name: string;
  version: string;
  doc_type: DocType;
  template?: {
    file: string;
    format: string;
    remote?: string;
  };
  id_pattern?: string;
  id_sequence_key?: string;
  structure?: {
    required_sections?: Array<{
      name: string;
      contains?: string[];
    }>;
    optional_sections?: Array<{
      name: string;
    }>;
  };
  validation?: {
    rules?: Array<{
      id: string;
      pattern?: string;
      message: string;
      suggestion?: string;
      docs?: string;
    }>;
    scripts?: Array<{
      path: string;
      description: string;
    }>;
  };
  output?: {
    default_path: string;
    naming: string;
  };
}

/**
 * Validation result
 */
export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  rule: string;
  message: string;
  line?: number;
  suggestion?: string;
  docs?: string;
}

export interface ValidationWarning {
  rule: string;
  message: string;
  line?: number;
}

/**
 * Template resolution result
 */
export interface TemplateResult {
  path: string;
  content: string;
  source: 'skill' | 'file-template';
  skill?: string;
}
