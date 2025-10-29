export class IdUtils {
  static generateUserId(): string {
    return `u-${Date.now().toString(36)}`;
  }

  static generateContainerId(userId: string): string {
    return `${userId}-c-${Date.now().toString(36)}`;
  }

  static generateAssetTypeId(containerId: string): string {
    return `${containerId}-t-${Date.now().toString(36)}`;
  }

  static generateSubtypeId(assetTypeId: string): string {
    return `${assetTypeId}-s-${Date.now().toString(36)}`;
  }

  static generateFieldId(parentId: string): string {
    return `${parentId}-f-${Date.now().toString(36)}`;
  }

  static generateAssetId(containerId: string): string {
    return `${containerId}-a-${Date.now().toString(36)}`;
  }

  static parseId(id: string): {
    userId?: string;
    containerId?: string;
    assetTypeId?: string;
    subtypeId?: string;
    fieldId?: string;
    assetId?: string;
  } {
    const parts = id.split('-');
    const result: any = {};
    
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      if (part === 'u') {
        result.userId = parts.slice(0, i + 1).join('-');
      } else if (part === 'c') {
        result.containerId = parts.slice(0, i + 1).join('-');
      } else if (part === 't') {
        result.assetTypeId = parts.slice(0, i + 1).join('-');
      } else if (part === 's') {
        result.subtypeId = parts.slice(0, i + 1).join('-');
      } else if (part === 'f') {
        result.fieldId = parts.slice(0, i + 1).join('-');
      } else if (part === 'a') {
        result.assetId = parts.slice(0, i + 1).join('-');
      }
    }
    
    return result;
  }

  static validateId(id: string): boolean {
    const pattern = /^[a-zA-Z0-9-]+$/;
    return pattern.test(id);
  }

  static validateUserId(id: string): boolean {
    return /^u-[a-zA-Z0-9]+$/.test(id);
  }

  static validateContainerId(id: string): boolean {
    return /^u-[a-zA-Z0-9]+-c-[a-zA-Z0-9]+$/.test(id);
  }

  static validateAssetTypeId(id: string): boolean {
    return /^u-[a-zA-Z0-9]+-c-[a-zA-Z0-9]+-t-[a-zA-Z0-9]+$/.test(id);
  }

  static validateSubtypeId(id: string): boolean {
    return /^u-[a-zA-Z0-9]+-c-[a-zA-Z0-9]+-t-[a-zA-Z0-9]+-s-[a-zA-Z0-9]+$/.test(id);
  }

  static validateFieldId(id: string): boolean {
    return /^u-[a-zA-Z0-9]+-c-[a-zA-Z0-9]+-t-[a-zA-Z0-9]+-s-[a-zA-Z0-9]+-f-[a-zA-Z0-9]+$/.test(id);
  }

  static validateAssetId(id: string): boolean {
    return /^u-[a-zA-Z0-9]+-c-[a-zA-Z0-9]+-a-[a-zA-Z0-9]+$/.test(id);
  }
} 