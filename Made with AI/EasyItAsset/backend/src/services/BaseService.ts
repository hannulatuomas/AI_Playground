import path from 'path';
import { promises as fs } from 'fs';

export abstract class BaseService {
  protected dataDir: string;

  constructor() {
    this.dataDir = path.join(process.cwd(), 'data');
  }

  protected async ensureDirectoryExists(dirPath: string): Promise<void> {
    try {
      await fs.mkdir(dirPath, { recursive: true });
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'EEXIST') {
        throw error;
      }
    }
  }

  protected async readJsonFile<T>(filePath: string): Promise<T | null> {
    try {
      const data = await fs.readFile(filePath, 'utf8');
      return JSON.parse(data) as T;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        return null;
      }
      throw error;
    }
  }

  protected async writeJsonFile<T>(filePath: string, data: T): Promise<void> {
    await fs.writeFile(filePath, JSON.stringify(data, null, 2), 'utf8');
  }

  protected async deleteFile(filePath: string): Promise<void> {
    try {
      await fs.unlink(filePath);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
        throw error;
      }
    }
  }

  protected async readDirectory(dirPath: string): Promise<string[]> {
    try {
      await this.ensureDirectoryExists(dirPath);
      return await fs.readdir(dirPath);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        return [];
      }
      throw error;
    }
  }

  public async cleanup(): Promise<void> {
    // Base cleanup method - can be overridden by derived classes if needed
    // By default, we don't need to do anything as file handles are closed automatically
    return Promise.resolve();
  }
} 