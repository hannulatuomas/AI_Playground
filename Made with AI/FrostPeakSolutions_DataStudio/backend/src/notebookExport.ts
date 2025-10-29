// Notebook Export API endpoint
import { Router } from 'express';
import { exportNotebook } from './services/export';
import { ExportFormat, ExportOptions, Notebook } from './typesExportImport';

const router = Router();

/**
 * POST /api/notebook/export
 * Body: {
 *   notebook: Notebook,
 *   options: ExportOptions
 * }
 * Returns exported notebook data in requested format (Content-Disposition: attachment)
 */
router.post('/', (req, res) => {
    const { notebook, options } = req.body;
    if (!notebook || !options || !options.format) {
        return res.status(400).json({ success: false, error: 'Missing notebook or options.format' });
    }
    try {
        // Validate format
        if (!Object.values(ExportFormat).includes(options.format)) {
            return res.status(400).json({ success: false, error: 'Invalid export format' });
        }
        const exportStr = exportNotebook(notebook, options);
        let mime = 'application/json';
        let ext = options.format;
        if (options.format === ExportFormat.JSON) mime = 'application/json';
        // Only JSON supported for now
        res.setHeader('Content-Type', mime);
        res.setHeader('Content-Disposition', `attachment; filename="notebook-export.${ext}"`);
        res.send(exportStr);
    } catch (err: any) {
        res.status(500).json({ success: false, error: err.message });
    }
});

export default router;
