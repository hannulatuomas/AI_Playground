import * as fs from 'fs';
import * as path from 'path';
import { logger } from './logger';

export class TransactionManager {
  private static instance: TransactionManager;
  private operations: Array<{ type: 'write' | 'delete', filePath: string, data?: any }> = [];
  private backupDir: string;

  private constructor() {
    this.backupDir = path.join(process.cwd(), 'data', 'backups');
    this.ensureBackupDirectory();
  }

  public static getInstance(): TransactionManager {
    if (!TransactionManager.instance) {
      TransactionManager.instance = new TransactionManager();
    }
    return TransactionManager.instance;
  }

  private ensureBackupDirectory(): void {
    if (!fs.existsSync(this.backupDir)) {
      fs.mkdirSync(this.backupDir, { recursive: true });
    }
  }

  public async beginTransaction(): Promise<void> {
    this.operations = [];
  }

  public async addOperation(type: 'write' | 'delete', filePath: string, data?: any): Promise<void> {
    this.operations.push({ type, filePath, data });
  }

  public async commit(): Promise<void> {
    try {
      // Create backups of all files to be modified
      for (const op of this.operations) {
        if (fs.existsSync(op.filePath)) {
          const backupPath = path.join(this.backupDir, `${path.basename(op.filePath)}_${Date.now()}.bak`);
          fs.copyFileSync(op.filePath, backupPath);
        }
      }

      // Execute all operations
      for (const op of this.operations) {
        if (op.type === 'write' && op.data !== undefined) {
          await fs.promises.writeFile(op.filePath, JSON.stringify(op.data, null, 2));
        } else if (op.type === 'delete') {
          await fs.promises.unlink(op.filePath);
        }
      }

      // Clear operations after successful commit
      this.operations = [];
    } catch (error) {
      await this.rollback();
      throw error;
    }
  }

  public async rollback(): Promise<void> {
    try {
      // Restore from backups
      const backupFiles = fs.readdirSync(this.backupDir);
      for (const backupFile of backupFiles) {
        if (backupFile.endsWith('.bak')) {
          const originalPath = path.join(process.cwd(), 'data', backupFile.replace(/_[\d]+\.bak$/, ''));
          const backupPath = path.join(this.backupDir, backupFile);
          fs.copyFileSync(backupPath, originalPath);
          fs.unlinkSync(backupPath);
        }
      }
    } catch (error) {
      logger.error('Error during rollback:', error);
      throw new Error('Failed to rollback transaction');
    } finally {
      this.operations = [];
    }
  }
} 