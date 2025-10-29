import { Router } from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs';

const uploadDir = path.join(__dirname, '../uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, uploadDir),
  filename: (_req, file, cb) => cb(null, `${Date.now()}-${file.originalname}`)
});
const upload = multer({ storage });

const router = Router();

// Upload CSV/XML file
router.post('/', upload.single('file'), (req, res) => {
  if (!req.file) return res.status(400).json({ success: false, error: 'No file uploaded' });
  res.json({ success: true, filename: req.file.filename, originalname: req.file.originalname });
});

// List uploaded files
router.get('/', (_req, res) => {
  fs.readdir(uploadDir, (err, files) => {
    if (err) return res.status(500).json({ success: false, error: err.message });
    res.json({ success: true, files });
  });
});

// Serve file contents for preview
router.get('/:filename', (req, res) => {
  const filename = req.params.filename;
  const filePath = path.join(uploadDir, filename);
  if (!fs.existsSync(filePath)) return res.status(404).send('File not found');
  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) return res.status(500).send('Failed to read file');
    res.type('text/plain').send(data);
  });
});

// DELETE /api/files/:filename
router.delete('/:filename', (req, res) => {
  const filename = req.params.filename;
  // Validate filename (no path traversal)
  if (!/^[\w\-. ]+$/.test(filename)) {
    return res.status(400).json({ success: false, error: 'Invalid filename' });
  }
  const filePath = path.join(uploadDir, filename);
  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ success: false, error: 'File not found' });
  }
  fs.unlink(filePath, err => {
    if (err) {
      return res.status(500).json({ success: false, error: 'Failed to delete file' });
    }
    res.json({ success: true });
  });
});

export default router;
