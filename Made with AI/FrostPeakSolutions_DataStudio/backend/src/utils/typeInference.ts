// Advanced type inference utility for MongoDB and Neo4j
// Strict TypeScript, no dependencies

/**
 * Infers a string type for a given value (deep, robust)
 * Types: null, boolean, integer, float, string, date, array, object, ObjectId, buffer, mixed
 * @param value Any JS value
 */
export function inferType(value: unknown): string {
  if (value === null) return 'null';
  if (value === undefined) return 'undefined';
  if (typeof value === 'boolean') return 'boolean';
  if (typeof value === 'number') return Number.isInteger(value) ? 'integer' : 'float';
  if (typeof value === 'string') {
    // ISO date detection
    if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(.\d+)?Z$/.test(value)) return 'date';
    return 'string';
  }
  if (typeof value === 'object') {
    if (Array.isArray(value)) {
      // Infer element type if possible
      const types = Array.from(new Set(value.map(inferType)));
      return types.length === 1 ? `array<${types[0]}>` : 'array<mixed>';
    }
    // MongoDB ObjectId
    if (value && typeof value === 'object' && value.constructor && value.constructor.name === 'ObjectId') {
      return 'ObjectId';
    }
    // Buffer/Binary
    if (typeof Buffer !== 'undefined' && value instanceof Buffer) return 'buffer';
    // Date
    if (value instanceof Date) return 'date';
    // Neo4j temporal types
    if (value.constructor && value.constructor.name && value.constructor.name.startsWith('Date')) return 'date';
    return 'object';
  }
  return typeof value;
}

/**
 * Merge multiple observed types into a single type string
 * If all types are the same, return that type; otherwise, return 'mixed' or array<mixed>
 */
export function mergeTypes(types: string[]): string {
  const unique = Array.from(new Set(types));
  if (unique.length === 1) return unique[0];
  // If all are array<...> of the same element type
  if (unique.every(t => t.startsWith('array<')) && new Set(unique.map(t => t.slice(6, -1))).size === 1) {
    return unique[0];
  }
  return 'mixed';
}
