// Environment utilities
export function isDev(): boolean {
  return process.env.NODE_ENV === 'development' || !app.isPackaged;
}

import { app } from 'electron';
