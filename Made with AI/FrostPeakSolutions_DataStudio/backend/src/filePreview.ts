import { Router } from 'express';
import path from 'path';
import fs from 'fs';
import readline from 'readline';

const uploadDir = path.join(__dirname, '../uploads');
const router = Router();

// GET /api/files/:filename/preview?lines=20
router.get('/:filename/preview', async (req, res) => {
  const filename = req.params.filename;
  const numLines = Math.max(1, parseInt(req.query.lines as string) || 20);
  if (!/^[\w\-. ]+$/.test(filename)) return res.status(400).json({ success: false, error: 'Invalid filename' });
  const filePath = path.join(uploadDir, filename);
  if (!fs.existsSync(filePath)) return res.status(404).json({ success: false, error: 'File not found' });

  // JSON preview logic
  if (filename.toLowerCase().endsWith('.json')) {
    try {
      const raw = fs.readFileSync(filePath, 'utf8');
      let jsonArr: any[];
      const flatten = (obj: any, prefix = '') => {
        const flat: any = {};
        for (const k in obj) {
          if (typeof obj[k] === 'object' && obj[k] !== null && !Array.isArray(obj[k])) {
            for (const subk in obj[k]) {
              flat[`${prefix}${k}.${subk}`] = obj[k][subk];
            }
          } else {
            flat[`${prefix}${k}`] = obj[k];
          }
        }
        return flat;
      };
      try {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          jsonArr = parsed;
        } else if (typeof parsed === 'object' && parsed !== null) {
          jsonArr = [parsed];
        } else {
          return res.json({ success: false, error: 'JSON root must be object or array' });
        }
      } catch (err) {
        return res.json({ success: false, error: 'Invalid JSON: ' + (err as Error).message });
      }
      const flatRows = jsonArr.map(obj => flatten(obj));
      const sample = flatRows.slice(0, numLines);
      return res.json({ success: true, rows: sample, totalRows: flatRows.length });
    } catch (err: any) {
      return res.status(500).json({ success: false, error: err.message });
    }
  }

  // Default: line-based preview for non-JSON
  const lines: string[] = [];
  let totalLines = 0;
  try {
    const rl = readline.createInterface({
      input: fs.createReadStream(filePath),
      crlfDelay: Infinity
    });
    for await (const line of rl) {
      if (lines.length < numLines) lines.push(line);
      totalLines++;
    }
    rl.close();
    return res.json({ success: true, lines, totalLines });
  } catch (err: any) {
    return res.status(500).json({ success: false, error: err.message });
  }
});

export default router;
