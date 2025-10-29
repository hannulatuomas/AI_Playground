export class IdUtils {
  private static readonly ID_SEPARATOR = '-';
  private static readonly USER_PREFIX = 'u';
  private static readonly CONTAINER_PREFIX = 'c';
  private static readonly ASSET_TYPE_PREFIX = 'at';
  private static readonly ASSET_PREFIX = 'a';
  private static readonly SUBTYPE_PREFIX = 'st';
  private static readonly FIELD_PREFIX = 'f';

  // ID validation patterns
  private static readonly ID_PATTERNS = {
    user: new RegExp(`^${this.USER_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+$`),
    container: new RegExp(`^${this.USER_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+${this.ID_SEPARATOR}${this.CONTAINER_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+$`),
    assetType: new RegExp(`^${this.USER_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+${this.ID_SEPARATOR}${this.CONTAINER_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+${this.ID_SEPARATOR}${this.ASSET_TYPE_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+$`),
    asset: new RegExp(`^${this.USER_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+${this.ID_SEPARATOR}${this.CONTAINER_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+${this.ID_SEPARATOR}${this.ASSET_TYPE_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+${this.ID_SEPARATOR}${this.ASSET_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+$`),
    subtype: new RegExp(`^${this.USER_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+${this.ID_SEPARATOR}${this.CONTAINER_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+${this.ID_SEPARATOR}${this.ASSET_TYPE_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+${this.ID_SEPARATOR}${this.SUBTYPE_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+${this.ID_SEPARATOR}${this.ASSET_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+$`),
    field: new RegExp(`^.*${this.ID_SEPARATOR}${this.FIELD_PREFIX}${this.ID_SEPARATOR}[a-zA-Z0-9]+$`)
  };

  // Generate a unique ID for a user
  static generateUserId(): string {
    return `${this.USER_PREFIX}${this.ID_SEPARATOR}${this.generateUniqueId()}`;
  }

  // Generate a container ID
  static generateContainerId(userId: string): string {
    if (!this.isValidId(userId, 'user')) {
      throw new Error('Invalid user ID format');
    }
    return `${userId}${this.ID_SEPARATOR}${this.CONTAINER_PREFIX}${this.ID_SEPARATOR}${this.generateUniqueId()}`;
  }

  // Generate an asset type ID
  static generateAssetTypeId(containerId: string): string {
    if (!this.isValidId(containerId, 'container')) {
      throw new Error('Invalid container ID format');
    }
    return `${containerId}${this.ID_SEPARATOR}${this.ASSET_TYPE_PREFIX}${this.ID_SEPARATOR}${this.generateUniqueId()}`;
  }

  // Generate an asset ID
  static generateAssetId(assetTypeId: string): string {
    if (!this.isValidId(assetTypeId, 'assetType')) {
      throw new Error('Invalid asset type ID format');
    }
    return `${assetTypeId}${this.ID_SEPARATOR}${this.ASSET_PREFIX}${this.ID_SEPARATOR}${this.generateUniqueId()}`;
  }

  // Generate a subtype ID
  static generateSubtypeId(assetTypeId: string): string {
    if (!this.isValidId(assetTypeId, 'assetType')) {
      throw new Error('Invalid asset type ID format');
    }
    const assetId = this.generateAssetId(assetTypeId);
    return `${assetTypeId}${this.ID_SEPARATOR}${this.SUBTYPE_PREFIX}${this.ID_SEPARATOR}${this.generateUniqueId()}${this.ID_SEPARATOR}${this.ASSET_PREFIX}${this.ID_SEPARATOR}${this.generateUniqueId()}`;
  }

  // Generate a field ID
  static generateFieldId(parentId: string): string {
    if (!this.isValidId(parentId)) {
      throw new Error('Invalid parent ID format');
    }
    return `${parentId}${this.ID_SEPARATOR}${this.FIELD_PREFIX}${this.ID_SEPARATOR}${this.generateUniqueId()}`;
  }

  // Generate a unique ID using timestamp and random number
  static generateUniqueId(): string {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substring(2, 8);
    return `${timestamp}${random}`;
  }

  // Validate an ID against a specific type
  static isValidId(id: string, type?: keyof typeof this.ID_PATTERNS): boolean {
    if (!type) {
      // Check against all patterns if no specific type is provided
      return Object.values(this.ID_PATTERNS).some(pattern => pattern.test(id));
    }
    return this.ID_PATTERNS[type].test(id);
  }

  // Get the user ID from any ID
  static getUserId(id: string): string | null {
    const parts = id.split(this.ID_SEPARATOR);
    if (parts[0] === this.USER_PREFIX) {
      return `${parts[0]}${this.ID_SEPARATOR}${parts[1]}`;
    }
    return null;
  }

  // Get the container ID from any ID
  static getContainerId(id: string): string | null {
    const parts = id.split(this.ID_SEPARATOR);
    const containerIndex = parts.indexOf(this.CONTAINER_PREFIX);
    if (containerIndex !== -1) {
      return parts.slice(0, containerIndex + 2).join(this.ID_SEPARATOR);
    }
    return null;
  }

  // Get the asset type ID from any ID
  static getAssetTypeId(id: string): string | null {
    const parts = id.split(this.ID_SEPARATOR);
    const assetTypeIndex = parts.indexOf(this.ASSET_TYPE_PREFIX);
    if (assetTypeIndex !== -1) {
      return parts.slice(0, assetTypeIndex + 2).join(this.ID_SEPARATOR);
    }
    return null;
  }

  // Get the asset ID from any ID
  static getAssetId(id: string): string | null {
    const parts = id.split(this.ID_SEPARATOR);
    const assetIndex = parts.indexOf(this.ASSET_PREFIX);
    if (assetIndex !== -1) {
      return parts.slice(0, assetIndex + 2).join(this.ID_SEPARATOR);
    }
    return null;
  }

  // Get the subtype ID from any ID
  static getSubtypeId(id: string): string | null {
    const parts = id.split(this.ID_SEPARATOR);
    const subtypeIndex = parts.indexOf(this.SUBTYPE_PREFIX);
    if (subtypeIndex !== -1) {
      return parts.slice(0, subtypeIndex + 2).join(this.ID_SEPARATOR);
    }
    return null;
  }

  // Parse an ID into its components
  static parseId(id: string): {
    userId?: string;
    containerId?: string;
    assetTypeId?: string;
    assetId?: string;
    subtypeId?: string;
  } {
    const result: any = {};
    result.userId = this.getUserId(id);
    result.containerId = this.getContainerId(id);
    result.assetTypeId = this.getAssetTypeId(id);
    result.assetId = this.getAssetId(id);
    result.subtypeId = this.getSubtypeId(id);
    return result;
  }

  // Get the parent ID of a given ID
  static getParentId(id: string): string | null {
    const parts = id.split(this.ID_SEPARATOR);
    if (parts.length <= 2) return null;
    
    // Remove the last two parts (prefix and unique ID)
    return parts.slice(0, -2).join(this.ID_SEPARATOR);
  }

  // Get the type of ID
  static getIdType(id: string): 'user' | 'container' | 'assetType' | 'asset' | 'subtype' | null {
    for (const [type, pattern] of Object.entries(this.ID_PATTERNS)) {
      if (pattern.test(id)) {
        return type as 'user' | 'container' | 'assetType' | 'asset' | 'subtype';
      }
    }
    return null;
  }

  // Generate multiple IDs of the same type
  static generateBulkIds(count: number, generator: () => string): string[] {
    const ids: string[] = [];
    for (let i = 0; i < count; i++) {
      ids.push(generator());
    }
    return ids;
  }

  // Generate multiple user IDs
  static generateBulkUserIds(count: number): string[] {
    return this.generateBulkIds(count, this.generateUserId);
  }

  // Generate multiple container IDs for a user
  static generateBulkContainerIds(userId: string, count: number): string[] {
    return this.generateBulkIds(count, () => this.generateContainerId(userId));
  }

  // Generate multiple asset type IDs for a container
  static generateBulkAssetTypeIds(containerId: string, count: number): string[] {
    return this.generateBulkIds(count, () => this.generateAssetTypeId(containerId));
  }

  // Generate multiple asset IDs for an asset type
  static generateBulkAssetIds(assetTypeId: string, count: number): string[] {
    return this.generateBulkIds(count, () => this.generateAssetId(assetTypeId));
  }

  // Generate multiple subtype IDs for an asset type
  static generateBulkSubtypeIds(assetTypeId: string, count: number): string[] {
    return this.generateBulkIds(count, () => this.generateSubtypeId(assetTypeId));
  }

  // Generate multiple field IDs for a parent
  static generateBulkFieldIds(parentId: string, count: number): string[] {
    return this.generateBulkIds(count, () => this.generateFieldId(parentId));
  }

  // Check if an ID belongs to a specific user
  static belongsToUser(id: string, userId: string): boolean {
    return this.getUserId(id) === userId;
  }

  // Check if an ID belongs to a specific container
  static belongsToContainer(id: string, containerId: string): boolean {
    return this.getContainerId(id) === containerId;
  }

  // Check if an ID belongs to a specific asset type
  static belongsToAssetType(id: string, assetTypeId: string): boolean {
    return this.getAssetTypeId(id) === assetTypeId;
  }

  // Check if an ID belongs to a specific asset
  static belongsToAsset(id: string, assetId: string): boolean {
    return this.getAssetId(id) === assetId;
  }

  // Check if an ID belongs to a specific subtype
  static belongsToSubtype(id: string, subtypeId: string): boolean {
    return this.getSubtypeId(id) === subtypeId;
  }

  // Extract user ID from container ID
  static getUserIdFromContainerId(containerId: string): string {
    if (!this.isValidId(containerId, 'container')) {
      throw new Error('Invalid container ID format');
    }
    const parts = containerId.split(this.ID_SEPARATOR);
    return `${parts[0]}${this.ID_SEPARATOR}${parts[1]}`;
  }
} 