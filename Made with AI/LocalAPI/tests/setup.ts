// Jest setup file for mocking Electron modules
import { createBetterSqlite3Mock } from './mocks/better-sqlite3.mock';

// Mock better-sqlite3 globally for all tests
jest.mock('better-sqlite3', () => createBetterSqlite3Mock());

// Mock Electron app module
jest.mock('electron', () => ({
  app: {
    getPath: jest.fn((name: string) => {
      // Return mock paths for testing
      const paths: Record<string, string> = {
        userData: '/tmp/localapi-test',
        appData: '/tmp/localapi-test',
        temp: '/tmp',
      };
      return paths[name] || '/tmp';
    }),
    on: jest.fn(),
    whenReady: jest.fn(() => Promise.resolve()),
  },
  BrowserWindow: jest.fn(),
  ipcMain: {
    handle: jest.fn(),
    on: jest.fn(),
  },
  ipcRenderer: {
    invoke: jest.fn(),
    on: jest.fn(),
  },
}));

// Mock swagger-parser
jest.mock('swagger-parser', () => {
  return {
    default: {
      validate: jest.fn((spec: any) => Promise.resolve(spec)),
    },
  };
});
