import * as fs from 'fs';
import * as path from 'path';

class Logger {
  private logFile: string;

  constructor() {
    const logsDir = path.join(__dirname, '..', '..', 'logs');
    if (!fs.existsSync(logsDir)) {
      fs.mkdirSync(logsDir);
    }
    this.logFile = path.join(logsDir, 'app.log');
  }

  private formatMessage(level: string, message: string, meta?: any): string {
    const timestamp = new Date().toISOString();
    const metaStr = meta ? JSON.stringify(meta) : '';
    return `[${timestamp}] ${level}: ${message} ${metaStr}\n`;
  }

  info(message: string, meta?: any) {
    const formattedMessage = this.formatMessage('INFO', message, meta);
    console.log(formattedMessage.trim());
    fs.appendFileSync(this.logFile, formattedMessage);
  }

  error(message: string, meta?: any) {
    const formattedMessage = this.formatMessage('ERROR', message, meta);
    console.error(formattedMessage.trim());
    fs.appendFileSync(this.logFile, formattedMessage);
  }

  warn(message: string, meta?: any) {
    const formattedMessage = this.formatMessage('WARN', message, meta);
    console.warn(formattedMessage.trim());
    fs.appendFileSync(this.logFile, formattedMessage);
  }
}

export const logger = new Logger(); 