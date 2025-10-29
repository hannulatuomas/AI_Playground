export const config = {
  port: process.env.PORT || 3001,
  dataDir: process.env.DATA_DIR || 'data',
  defaultUserId: process.env.DEFAULT_USER_ID || 'default_user',
  csvHeaders: {
    containers: ['id', 'name', 'description', 'ownerId', 'createdAt', 'updatedAt'],
    assetTypes: ['id', 'name', 'label', 'containerId', 'fields', 'subtypes'],
    assets: ['id', 'name', 'containerId', 'assetTypeId', 'assetSubTypeId', 'values', 'createdAt', 'updatedAt'],
    subtypes: ['id', 'name', 'label', 'containerId', 'parentTypeId', 'fields', 'hiddenFields', 'overriddenFields']
  }
}; 