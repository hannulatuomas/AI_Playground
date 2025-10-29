// Secrets Service for secure credential storage using keytar
// Uses OS-level credential management (Windows Credential Manager, macOS Keychain, Linux Secret Service)

const SERVICE_NAME = 'LocalAPI';

interface SecretMetadata {
  key: string;
  scope: string;
  description?: string;
  createdAt: Date;
}

export class SecretsService {
  private keytar: any = null;
  private available: boolean = false;
  private metadata: Map<string, SecretMetadata> = new Map();

  constructor() {
    this.initializeKeytar();
  }

  /**
   * Initialize keytar (optional dependency)
   */
  private async initializeKeytar() {
    try {
      this.keytar = require('keytar');
      this.available = true;
      console.log('Keytar initialized successfully - using OS credential storage');
    } catch (error) {
      console.warn('Keytar not available - secrets will be stored in database (less secure)');
      this.available = false;
    }
  }

  /**
   * Check if keytar is available
   */
  isAvailable(): boolean {
    return this.available;
  }

  /**
   * Set a secret in the OS credential store
   */
  async setSecret(scope: string, key: string, value: string, description?: string): Promise<boolean> {
    if (!this.available || !this.keytar) {
      console.warn('Keytar not available, secret not stored securely');
      return false;
    }

    try {
      const account = `${scope}:${key}`;
      await this.keytar.setPassword(SERVICE_NAME, account, value);
      
      // Store metadata
      this.metadata.set(account, {
        key,
        scope,
        description,
        createdAt: new Date(),
      });

      console.log(`Secret stored securely: ${scope}:${key}`);
      return true;
    } catch (error: any) {
      console.error('Failed to store secret:', error.message);
      return false;
    }
  }

  /**
   * Get a secret from the OS credential store
   */
  async getSecret(scope: string, key: string): Promise<string | null> {
    if (!this.available || !this.keytar) {
      return null;
    }

    try {
      const account = `${scope}:${key}`;
      const password = await this.keytar.getPassword(SERVICE_NAME, account);
      return password;
    } catch (error: any) {
      console.error('Failed to retrieve secret:', error.message);
      return null;
    }
  }

  /**
   * Delete a secret from the OS credential store
   */
  async deleteSecret(scope: string, key: string): Promise<boolean> {
    if (!this.available || !this.keytar) {
      return false;
    }

    try {
      const account = `${scope}:${key}`;
      const result = await this.keytar.deletePassword(SERVICE_NAME, account);
      
      // Remove metadata
      this.metadata.delete(account);
      
      console.log(`Secret deleted: ${scope}:${key}`);
      return result;
    } catch (error: any) {
      console.error('Failed to delete secret:', error.message);
      return false;
    }
  }

  /**
   * Find all credentials for the service
   */
  async findCredentials(): Promise<Array<{ account: string; password: string }>> {
    if (!this.available || !this.keytar) {
      return [];
    }

    try {
      const credentials = await this.keytar.findCredentials(SERVICE_NAME);
      return credentials || [];
    } catch (error: any) {
      console.error('Failed to find credentials:', error.message);
      return [];
    }
  }

  /**
   * Get all secrets for a specific scope
   */
  async getSecretsByScope(scope: string): Promise<Map<string, string>> {
    const secrets = new Map<string, string>();
    
    if (!this.available || !this.keytar) {
      return secrets;
    }

    try {
      const credentials = await this.findCredentials();
      
      for (const cred of credentials) {
        const [credScope, key] = cred.account.split(':');
        if (credScope === scope) {
          secrets.set(key, cred.password);
        }
      }
      
      return secrets;
    } catch (error: any) {
      console.error('Failed to get secrets by scope:', error.message);
      return secrets;
    }
  }

  /**
   * Delete all secrets for a specific scope
   */
  async deleteSecretsByScope(scope: string): Promise<number> {
    if (!this.available || !this.keytar) {
      return 0;
    }

    let deletedCount = 0;

    try {
      const credentials = await this.findCredentials();
      
      for (const cred of credentials) {
        const [credScope, key] = cred.account.split(':');
        if (credScope === scope) {
          const deleted = await this.deleteSecret(scope, key);
          if (deleted) deletedCount++;
        }
      }
      
      console.log(`Deleted ${deletedCount} secrets from scope: ${scope}`);
      return deletedCount;
    } catch (error: any) {
      console.error('Failed to delete secrets by scope:', error.message);
      return deletedCount;
    }
  }

  /**
   * Check if a secret exists
   */
  async hasSecret(scope: string, key: string): Promise<boolean> {
    const value = await this.getSecret(scope, key);
    return value !== null;
  }

  /**
   * Update a secret (same as set)
   */
  async updateSecret(scope: string, key: string, value: string): Promise<boolean> {
    return await this.setSecret(scope, key, value);
  }

  /**
   * Get metadata for a secret
   */
  getMetadata(scope: string, key: string): SecretMetadata | undefined {
    const account = `${scope}:${key}`;
    return this.metadata.get(account);
  }

  /**
   * Clear all secrets (use with caution!)
   */
  async clearAll(): Promise<number> {
    if (!this.available || !this.keytar) {
      return 0;
    }

    let deletedCount = 0;

    try {
      const credentials = await this.findCredentials();
      
      for (const cred of credentials) {
        const [scope, key] = cred.account.split(':');
        const deleted = await this.deleteSecret(scope, key);
        if (deleted) deletedCount++;
      }
      
      this.metadata.clear();
      console.log(`Cleared all ${deletedCount} secrets`);
      return deletedCount;
    } catch (error: any) {
      console.error('Failed to clear all secrets:', error.message);
      return deletedCount;
    }
  }

  /**
   * Export secrets for backup (encrypted)
   */
  async exportSecrets(): Promise<Array<{ scope: string; key: string; value: string }>> {
    const exported: Array<{ scope: string; key: string; value: string }> = [];

    if (!this.available || !this.keytar) {
      return exported;
    }

    try {
      const credentials = await this.findCredentials();
      
      for (const cred of credentials) {
        const [scope, key] = cred.account.split(':');
        exported.push({
          scope,
          key,
          value: cred.password,
        });
      }
      
      return exported;
    } catch (error: any) {
      console.error('Failed to export secrets:', error.message);
      return exported;
    }
  }

  /**
   * Import secrets from backup
   */
  async importSecrets(secrets: Array<{ scope: string; key: string; value: string }>): Promise<number> {
    let importedCount = 0;

    for (const secret of secrets) {
      const success = await this.setSecret(secret.scope, secret.key, secret.value);
      if (success) importedCount++;
    }

    console.log(`Imported ${importedCount} secrets`);
    return importedCount;
  }
}

// Singleton instance
let secretsServiceInstance: SecretsService | null = null;

export function getSecretsService(): SecretsService {
  if (!secretsServiceInstance) {
    secretsServiceInstance = new SecretsService();
  }
  return secretsServiceInstance;
}
