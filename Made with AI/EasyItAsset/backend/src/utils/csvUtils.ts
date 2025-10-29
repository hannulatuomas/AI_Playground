import { parse } from 'csv-parse/sync';
import { stringify } from 'csv-stringify/sync';
import * as fs from 'fs';
import * as path from 'path';

export const readCsvFile = (filePath: string): any[] => {
  if (!fs.existsSync(filePath)) {
    return [];
  }
  const content = fs.readFileSync(filePath, 'utf-8');
  return parse(content, { columns: true, skip_empty_lines: true });
};

export const writeCsvFile = (filePath: string, data: any[], headers: string[]): void => {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  const content = stringify(data, { header: true, columns: headers });
  fs.writeFileSync(filePath, content);
};

export const ensureFileExists = (filePath: string, headers: string[]): void => {
  if (!fs.existsSync(filePath)) {
    writeCsvFile(filePath, [], headers);
  }
}; 