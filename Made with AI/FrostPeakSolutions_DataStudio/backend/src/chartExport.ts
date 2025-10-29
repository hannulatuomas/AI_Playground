// Chart Export API endpoint
import { Router } from 'express';
import { exportChartData } from './services/export';
import { ExportFormat, ExportOptions, QueryResult } from './typesExportImport';

const router = Router();

/**
 * POST /api/chart/export
 * Body: {
 *   result: QueryResult,
 *   options: ExportOptions
 * }
 * Returns exported chart data in requested format (Content-Disposition: attachment)
 */
router.post('/', (req, res) => {
    const { result, options } = req.body;
    if (!result || !options || !options.format) {
        return res.status(400).json({ success: false, error: 'Missing result or options.format' });
    }
    try {
        // Validate format
        if (!Object.values(ExportFormat).includes(options.format)) {
            return res.status(400).json({ success: false, error: 'Invalid export format' });
        }
        const exportStr = exportChartData(result, options);
        let mime = 'text/plain';
        let ext = options.format;
        if (options.format === ExportFormat.JSON) mime = 'application/json';
        if (options.format === ExportFormat.CSV) mime = 'text/csv';
        if (options.format === ExportFormat.XML) mime = 'application/xml';
        res.setHeader('Content-Type', mime);
        res.setHeader('Content-Disposition', `attachment; filename="chart-data.${ext}"`);
        res.send(exportStr);
    } catch (err: any) {
        res.status(500).json({ success: false, error: err.message });
    }
});

export default router;
