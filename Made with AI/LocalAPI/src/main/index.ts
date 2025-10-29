// Electron main process entry point
import { app, BrowserWindow } from 'electron';
import * as path from 'path';
import * as fs from 'fs';
import { isDev } from './utils/environment';
import { registerIpcHandlers } from './ipc/handlers';
import { getDatabaseService } from './services/DatabaseService';

let mainWindow: BrowserWindow | null = null;
let loadingWindow: BrowserWindow | null = null;

function createLoadingWindow(): void {
  const appPath = app.getAppPath();
  const iconPath = path.join(appPath, 'build', 'icon.png');
  
  loadingWindow = new BrowserWindow({
    width: 400,
    height: 300,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    icon: fs.existsSync(iconPath) ? iconPath : undefined,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  loadingWindow.loadFile(path.join(__dirname, 'loading.html'));
  loadingWindow.center();
}

function updateLoadingProgress(status: string, progress: number): void {
  if (loadingWindow && !loadingWindow.isDestroyed()) {
    loadingWindow.webContents.send('loading-progress', { status, progress });
  }
}

function closeLoadingWindow(): void {
  if (loadingWindow && !loadingWindow.isDestroyed()) {
    loadingWindow.close();
    loadingWindow = null;
  }
}

function createWindow(): void {
  const appPath = app.getAppPath();
  const iconPath = path.join(appPath, 'build', 'icon.png');
  const iconExists = fs.existsSync(iconPath);
  
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    icon: iconExists ? iconPath : undefined,
    webPreferences: {
      preload: path.join(__dirname, '../../preload/preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
    show: false,
  });

  if (isDev()) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    updateLoadingProgress('Ready!', 100);
    setTimeout(() => {
      closeLoadingWindow();
      mainWindow?.show();
    }, 500);
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Show loading window as early as possible
app.on('ready', () => {
  createLoadingWindow();
});

app.whenReady().then(async () => {
  // Wait for loading window to be ready
  await new Promise(resolve => setTimeout(resolve, 200));
  updateLoadingProgress('Initializing database...', 20);

  // Small delay to show loading window
  await new Promise(resolve => setTimeout(resolve, 100));

  // Initialize database
  try {
    getDatabaseService();
    console.log('Database service initialized');
    updateLoadingProgress('Database ready', 40);
  } catch (error) {
    console.error('Failed to initialize database:', error);
    updateLoadingProgress('Database initialization failed', 40);
  }

  await new Promise(resolve => setTimeout(resolve, 100));
  updateLoadingProgress('Registering IPC handlers...', 60);

  // Register IPC handlers
  registerIpcHandlers();
  
  await new Promise(resolve => setTimeout(resolve, 100));
  updateLoadingProgress('Loading application...', 80);

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed (including on macOS)
app.on('window-all-closed', () => {
  // Close database connection
  try {
    const db = getDatabaseService();
    db.close();
  } catch (error) {
    console.error('Error closing database:', error);
  }
  
  // Exit cleanly
  app.quit();
  process.exit(0);
});
