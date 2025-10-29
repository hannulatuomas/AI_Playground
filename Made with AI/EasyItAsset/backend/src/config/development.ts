import { config as defaultConfig } from './default';

export const config = {
  ...defaultConfig,
  port: 3001,
  dataDir: 'data',
  defaultUserId: 'development_user'
}; 