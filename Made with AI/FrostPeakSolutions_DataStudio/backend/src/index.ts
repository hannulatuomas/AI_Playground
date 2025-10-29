import express from 'express';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json());

app.get('/api/health', (req, res) => res.json({ status: 'ok' }));
import connectionsRouter from './connections';
import queryRouter from './query';
import queryExportRouter from './queryExport';
import notebookExportRouter from './notebookExport';
import chartExportRouter from './chartExport';
import fileUploadRouter from './fileUpload';
import filePreviewRouter from './filePreview';
import schemaRouter from './schema';

app.use('/api/connections', connectionsRouter);
app.use('/api/query', queryRouter);
app.use('/api/query/export', queryExportRouter);
app.use('/api/files', fileUploadRouter);
app.use('/api/files', filePreviewRouter);
app.use('/api/schema', schemaRouter);
app.use('/api/notebook/export', notebookExportRouter);
app.use('/api/chart/export', chartExportRouter);

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`Backend running on port ${PORT}`));
