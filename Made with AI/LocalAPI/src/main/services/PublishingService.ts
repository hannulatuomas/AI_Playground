/**
 * PublishingService - API Documentation Publishing
 * 
 * Handles publishing documentation to various targets:
 * - Local HTTP server
 * - Static file directory
 * - PDF export
 */

import * as http from 'http';
import * as fs from 'fs';
import * as path from 'path';
import type { GeneratedDocumentation } from './DocumentationGeneratorService';

export interface PublishOptions {
  target: 'server' | 'directory' | 'pdf';
  port?: number;
  directory?: string;
  filename?: string;
}

export interface PublishResult {
  success: boolean;
  url?: string;
  path?: string;
  error?: string;
}

export class PublishingService {
  private server?: http.Server;
  private serverPort?: number;

  /**
   * Publish documentation
   */
  async publish(doc: GeneratedDocumentation, options: PublishOptions): Promise<PublishResult> {
    try {
      switch (options.target) {
        case 'server':
          return await this.publishToServer(doc, options.port || 3000);
        case 'directory':
          return await this.publishToDirectory(doc, options.directory || './docs');
        case 'pdf':
          return await this.publishToPDF(doc, options.filename || 'api-docs.pdf');
        default:
          return {
            success: false,
            error: `Unknown target: ${options.target}`,
          };
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Publish to local HTTP server
   */
  private async publishToServer(doc: GeneratedDocumentation, port: number): Promise<PublishResult> {
    // Stop existing server if running
    if (this.server) {
      await this.stopServer();
    }

    return new Promise((resolve) => {
      this.server = http.createServer((req, res) => {
        const url = req.url || '/';

        if (url === '/' || url === '/index.html') {
          res.writeHead(200, { 'Content-Type': 'text/html' });
          res.end(doc.html);
        } else if (url === '/explorer.js' && doc.js) {
          res.writeHead(200, { 'Content-Type': 'application/javascript' });
          res.end(doc.js);
        } else {
          res.writeHead(404, { 'Content-Type': 'text/plain' });
          res.end('Not Found');
        }
      });

      this.server.listen(port, () => {
        this.serverPort = port;
        resolve({
          success: true,
          url: `http://localhost:${port}`,
        });
      });

      this.server.on('error', (error) => {
        resolve({
          success: false,
          error: error.message,
        });
      });
    });
  }

  /**
   * Stop the HTTP server
   */
  async stopServer(): Promise<void> {
    return new Promise((resolve) => {
      if (this.server) {
        this.server.close(() => {
          this.server = undefined;
          this.serverPort = undefined;
          resolve();
        });
      } else {
        resolve();
      }
    });
  }

  /**
   * Check if server is running
   */
  isServerRunning(): boolean {
    return !!this.server;
  }

  /**
   * Get server URL
   */
  getServerUrl(): string | null {
    return this.serverPort ? `http://localhost:${this.serverPort}` : null;
  }

  /**
   * Publish to static file directory
   */
  private async publishToDirectory(doc: GeneratedDocumentation, directory: string): Promise<PublishResult> {
    try {
      // Create directory if it doesn't exist
      if (!fs.existsSync(directory)) {
        fs.mkdirSync(directory, { recursive: true });
      }

      // Write HTML file
      const htmlPath = path.join(directory, 'index.html');
      fs.writeFileSync(htmlPath, doc.html);

      // Write JS file if present
      if (doc.js) {
        const jsPath = path.join(directory, 'explorer.js');
        fs.writeFileSync(jsPath, doc.js);
      }

      return {
        success: true,
        path: path.resolve(directory),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to write files',
      };
    }
  }

  /**
   * Publish to PDF
   * Note: This is a simplified implementation. For production, consider using puppeteer or similar
   */
  private async publishToPDF(doc: GeneratedDocumentation, filename: string): Promise<PublishResult> {
    try {
      // For now, we'll create an HTML file that can be printed to PDF
      // In a real implementation, you'd use puppeteer or similar to generate actual PDF
      
      const pdfHtml = this.preparePDFHtml(doc.html);
      const outputPath = path.resolve(filename.replace('.pdf', '.html'));
      
      fs.writeFileSync(outputPath, pdfHtml);

      return {
        success: true,
        path: outputPath,
        error: 'PDF export created as HTML. Use browser "Print to PDF" or integrate puppeteer for automatic PDF generation.',
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create PDF',
      };
    }
  }

  /**
   * Prepare HTML for PDF printing
   */
  private preparePDFHtml(html: string): string {
    // Add print-specific CSS
    const printCss = `
<style>
@media print {
  body { font-size: 12pt; }
  .sidebar { display: none; }
  .content { max-width: 100%; }
  .operation { page-break-inside: avoid; }
  .header { page-break-after: avoid; }
  a { text-decoration: none; color: #000; }
  pre { page-break-inside: avoid; }
}
</style>`;

    return html.replace('</head>', `${printCss}</head>`);
  }

  /**
   * Publish to multiple targets
   */
  async publishMultiple(
    doc: GeneratedDocumentation,
    targets: PublishOptions[]
  ): Promise<PublishResult[]> {
    const results: PublishResult[] = [];

    for (const target of targets) {
      const result = await this.publish(doc, target);
      results.push(result);
    }

    return results;
  }

  /**
   * Get publish status
   */
  getStatus(): {
    serverRunning: boolean;
    serverUrl: string | null;
  } {
    return {
      serverRunning: this.isServerRunning(),
      serverUrl: this.getServerUrl(),
    };
  }

  /**
   * Clean up resources
   */
  async cleanup(): Promise<void> {
    await this.stopServer();
  }
}
