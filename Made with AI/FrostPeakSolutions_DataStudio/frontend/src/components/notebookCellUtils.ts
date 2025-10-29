// notebookCellUtils.ts

export function validateSql(sql: string): string | null {
  if (!sql.trim()) return 'SQL query cannot be empty.';
  if (!/\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b/i.test(sql)) {
    return 'Query should start with a valid SQL command (SELECT, INSERT, etc).';
  }
  return null;
}

export function getCurrentWord(val: string, cursor: number): string {
  const left = val.slice(0, cursor);
  const match = left.match(/([\w.]+)$/);
  return match ? match[1] : '';
}

export function getSuggestions(schemaTables?: any[]): string[] {
  const SQL_KEYWORDS = [
    'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'JOIN',
    'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET', 'AS', 'AND', 'OR', 'NOT', 'IN', 'IS',
    'NULL', 'DISTINCT', 'COUNT', 'AVG', 'SUM', 'MIN', 'MAX', 'ON', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER'
  ];
  let sugg: string[] = [...SQL_KEYWORDS];
  if (schemaTables && schemaTables.length) {
    sugg = sugg.concat(schemaTables.map((t: any) => t.table));
    sugg = sugg.concat(schemaTables.flatMap((t: any) => t.columns.map((col: any) => typeof col === 'string' ? col : col.name)));
  }
  return Array.from(new Set(sugg));
}
