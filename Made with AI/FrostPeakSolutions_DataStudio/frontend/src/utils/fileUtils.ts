// Utility for file workflow (temporary ID generator until backend provides IDs)
export function generateFileId(filename: string, type: string): string {
  // For now, create a deterministic ID based on filename and type
  // (Replace with backend-provided IDs when available)
  return `${type}::${filename}`;
}
