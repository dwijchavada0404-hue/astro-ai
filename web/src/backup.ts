export type AstroAiBackup = {
  export_version: number;
  birth_profiles?: unknown[];
  conversations?: unknown[];
  [key: string]: unknown;
};

export function parseAstroAiBackup(text: string): AstroAiBackup {
  let value: unknown;
  try {
    value = JSON.parse(text);
  } catch {
    throw new Error("This file is not valid JSON.");
  }
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("This is not a valid AstroAI backup file.");
  }
  const backup = value as AstroAiBackup;
  if (backup.export_version !== 1) {
    throw new Error("Only AstroAI export version 1 backups can be restored.");
  }
  if (backup.birth_profiles !== undefined && !Array.isArray(backup.birth_profiles)) {
    throw new Error("This AstroAI backup has an invalid birth_profiles section.");
  }
  if (backup.conversations !== undefined && !Array.isArray(backup.conversations)) {
    throw new Error("This AstroAI backup has an invalid conversations section.");
  }
  return backup;
}
