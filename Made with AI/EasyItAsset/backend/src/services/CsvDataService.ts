import { IDataService } from './IDataService';
import { IContainer } from '../types/Container';
import { IAssetTypeConfig, IAssetSubTypeConfig } from '../types/FieldConfig';
import { IAsset } from '../types/Asset';
import * as fs from 'fs';
import * as path from 'path';
import { parse } from 'csv-parse/sync';
import { stringify } from 'csv-stringify/sync';

export class CsvDataService implements IDataService {
  private readonly dataDir: string;
  private readonly containersFile: string;

  constructor(private readonly userId: string) {
    this.dataDir = path.join(__dirname, '..', '..', 'data');
    
    // Ensure data directory exists
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }

    // Initialize containers file with user ID prefix
    this.containersFile = path.join(this.dataDir, `${userId}_containers.csv`);

    // Initialize containers file with headers if it doesn't exist
    if (!fs.existsSync(this.containersFile)) {
      fs.writeFileSync(this.containersFile, 'id,name,description,ownerId,assetTypeConfigs,assets,createdAt,updatedAt\n');
    }
  }

  private getAssetTypesFile(containerId: string): string {
    return path.join(this.dataDir, `${this.userId}_${containerId}_asset_types.csv`);
  }

  private getSubTypesFile(containerId: string): string {
    return path.join(this.dataDir, `${this.userId}_${containerId}_subtypes.csv`);
  }

  private getAssetsFile(containerId: string): string {
    return path.join(this.dataDir, `${this.userId}_${containerId}_assets.csv`);
  }

  private ensureFileExists(filePath: string, headers: string): void {
    if (!fs.existsSync(filePath)) {
      fs.writeFileSync(filePath, headers);
    }
  }

  // Container operations
  async saveContainer(container: IContainer): Promise<void> {
    const content = fs.readFileSync(this.containersFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    records.push({
      ...container,
      assetTypeConfigs: JSON.stringify(container.assetTypeConfigs),
      assets: JSON.stringify(container.assets),
      createdAt: container.createdAt.toISOString(),
      updatedAt: container.updatedAt.toISOString()
    });
    fs.writeFileSync(this.containersFile, stringify(records, { header: true }));

    // Initialize container-specific files
    const assetTypesFile = this.getAssetTypesFile(container.id);
    const subTypesFile = this.getSubTypesFile(container.id);
    const assetsFile = this.getAssetsFile(container.id);

    this.ensureFileExists(assetTypesFile, 'id,name,description,ownerId,assetTypeConfigs,assets,createdAt,updatedAt\n');
    this.ensureFileExists(subTypesFile, 'id,containerId,parentTypeId,name,label,fields,createdAt,updatedAt\n');
    this.ensureFileExists(assetsFile, 'id,containerId,typeId,subTypeId,name,description,fields,createdAt,updatedAt\n');
  }

  async getContainer(id: string): Promise<IContainer | null> {
    const content = fs.readFileSync(this.containersFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    const record = records.find((r: any) => r.id === id);
    if (!record) return null;
    return {
      ...record,
      assetTypeConfigs: JSON.parse(record.assetTypeConfigs || '[]'),
      assets: JSON.parse(record.assets || '[]'),
      createdAt: new Date(record.createdAt),
      updatedAt: new Date(record.updatedAt)
    };
  }

  async getContainersByOwner(ownerId: string): Promise<IContainer[]> {
    const content = fs.readFileSync(this.containersFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    return records
      .filter((r: any) => r.ownerId === ownerId)
      .map((r: any) => ({
        ...r,
        assetTypeConfigs: JSON.parse(r.assetTypeConfigs || '[]'),
        assets: JSON.parse(r.assets || '[]'),
        createdAt: new Date(r.createdAt),
        updatedAt: new Date(r.updatedAt)
      }));
  }

  async updateContainer(id: string, container: Partial<IContainer>): Promise<void> {
    const content = fs.readFileSync(this.containersFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    const index = records.findIndex((r: any) => r.id === id);
    if (index === -1) throw new Error('Container not found');
    records[index] = {
      ...records[index],
      ...container,
      assetTypeConfigs: JSON.stringify(container.assetTypeConfigs || JSON.parse(records[index].assetTypeConfigs || '[]')),
      assets: JSON.stringify(container.assets || JSON.parse(records[index].assets || '[]')),
      updatedAt: new Date().toISOString()
    };
    fs.writeFileSync(this.containersFile, stringify(records, { header: true }));
  }

  async deleteContainer(id: string): Promise<void> {
    const content = fs.readFileSync(this.containersFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    const filteredRecords = records.filter((r: any) => r.id !== id);
    fs.writeFileSync(this.containersFile, stringify(filteredRecords, { header: true }));

    // Delete container-specific files
    const assetTypesFile = this.getAssetTypesFile(id);
    const subTypesFile = this.getSubTypesFile(id);
    const assetsFile = this.getAssetsFile(id);

    if (fs.existsSync(assetTypesFile)) fs.unlinkSync(assetTypesFile);
    if (fs.existsSync(subTypesFile)) fs.unlinkSync(subTypesFile);
    if (fs.existsSync(assetsFile)) fs.unlinkSync(assetsFile);
  }

  // Asset type operations
  async saveAssetTypeConfig(containerId: string, config: IAssetTypeConfig): Promise<void> {
    const assetTypesFile = this.getAssetTypesFile(containerId);
    this.ensureFileExists(assetTypesFile, 'id,containerId,name,label,fields,subtypes,createdAt,updatedAt\n');

    const content = fs.readFileSync(assetTypesFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    records.push({
      ...config,
      fields: JSON.stringify(config.fields),
      subtypes: JSON.stringify(config.subtypes),
      createdAt: config.createdAt.toISOString(),
      updatedAt: config.updatedAt.toISOString()
    });
    fs.writeFileSync(assetTypesFile, stringify(records, { header: true }));
  }

  async getAssetTypeConfig(containerId: string, typeName: string): Promise<IAssetTypeConfig | null> {
    const assetTypesFile = this.getAssetTypesFile(containerId);
    if (!fs.existsSync(assetTypesFile)) return null;

    const content = fs.readFileSync(assetTypesFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    const record = records.find((r: any) => r.containerId === containerId && r.name === typeName);
    if (!record) return null;
    return {
      ...record,
      fields: JSON.parse(record.fields || '[]'),
      createdAt: new Date(record.createdAt),
      updatedAt: new Date(record.updatedAt)
    };
  }

  async updateAssetTypeConfig(containerId: string, typeName: string, config: IAssetTypeConfig): Promise<void> {
    const assetTypesFile = this.getAssetTypesFile(containerId);
    if (!fs.existsSync(assetTypesFile)) throw new Error('Asset type not found');

    const content = fs.readFileSync(assetTypesFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    const index = records.findIndex((r: any) => r.containerId === containerId && r.name === typeName);
    if (index === -1) throw new Error('Asset type not found');
    records[index] = {
      ...config,
      fields: JSON.stringify(config.fields),
      updatedAt: new Date().toISOString()
    };
    fs.writeFileSync(assetTypesFile, stringify(records, { header: true }));
  }

  async deleteAssetTypeConfig(containerId: string, typeName: string): Promise<void> {
    const assetTypesFile = this.getAssetTypesFile(containerId);
    if (!fs.existsSync(assetTypesFile)) return;

    const content = fs.readFileSync(assetTypesFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    const filteredRecords = records.filter((r: any) => !(r.containerId === containerId && r.name === typeName));
    fs.writeFileSync(assetTypesFile, stringify(filteredRecords, { header: true }));
  }

  // Asset subtype operations
  async saveAssetSubTypeConfig(containerId: string, parentTypeId: string, config: IAssetSubTypeConfig): Promise<void> {
    const subTypesFile = this.getSubTypesFile(containerId);
    this.ensureFileExists(subTypesFile, 'id,containerId,parentTypeId,name,label,fields,createdAt,updatedAt\n');

    const content = fs.readFileSync(subTypesFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    records.push({
      ...config,
      fields: JSON.stringify(config.fields),
      createdAt: config.createdAt.toISOString(),
      updatedAt: config.updatedAt.toISOString()
    });
    fs.writeFileSync(subTypesFile, stringify(records, { header: true }));
  }

  async getAssetSubTypeConfig(containerId: string, parentTypeId: string, subTypeName: string): Promise<IAssetSubTypeConfig | null> {
    const subTypesFile = this.getSubTypesFile(containerId);
    if (!fs.existsSync(subTypesFile)) return null;

    const content = fs.readFileSync(subTypesFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    const record = records.find((r: any) => 
      r.containerId === containerId && 
      r.parentTypeId === parentTypeId && 
      r.name === subTypeName
    );
    if (!record) return null;
    return {
      ...record,
      fields: JSON.parse(record.fields || '[]'),
      createdAt: new Date(record.createdAt),
      updatedAt: new Date(record.updatedAt)
    };
  }

  async updateAssetSubTypeConfig(containerId: string, parentTypeId: string, subTypeName: string, config: IAssetSubTypeConfig): Promise<void> {
    const subTypesFile = this.getSubTypesFile(containerId);
    if (!fs.existsSync(subTypesFile)) throw new Error('Asset subtype not found');

    const content = fs.readFileSync(subTypesFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    const index = records.findIndex((r: any) => 
      r.containerId === containerId && 
      r.parentTypeId === parentTypeId && 
      r.name === subTypeName
    );
    if (index === -1) throw new Error('Asset subtype not found');
    records[index] = {
      ...config,
      fields: JSON.stringify(config.fields),
      updatedAt: new Date().toISOString()
    };
    fs.writeFileSync(subTypesFile, stringify(records, { header: true }));
  }

  async deleteAssetSubTypeConfig(containerId: string, parentTypeId: string, subTypeName: string): Promise<void> {
    const subTypesFile = this.getSubTypesFile(containerId);
    if (!fs.existsSync(subTypesFile)) return;

    const content = fs.readFileSync(subTypesFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    const filteredRecords = records.filter((r: any) => 
      !(r.containerId === containerId && 
        r.parentTypeId === parentTypeId && 
        r.name === subTypeName)
    );
    fs.writeFileSync(subTypesFile, stringify(filteredRecords, { header: true }));
  }

  // Asset operations
  async saveAsset(containerId: string, asset: IAsset): Promise<void> {
    const assetsFile = this.getAssetsFile(containerId);
    this.ensureFileExists(assetsFile, 'id,containerId,typeId,subTypeId,name,description,fields,createdAt,updatedAt\n');

    const content = fs.readFileSync(assetsFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    records.push({
      ...asset,
      values: JSON.stringify(asset.values),
      createdAt: asset.createdAt.toISOString(),
      updatedAt: asset.updatedAt.toISOString()
    });
    fs.writeFileSync(assetsFile, stringify(records, { header: true }));
  }

  async getAsset(containerId: string, assetId: string): Promise<IAsset | null> {
    const assetsFile = this.getAssetsFile(containerId);
    if (!fs.existsSync(assetsFile)) return null;

    const content = fs.readFileSync(assetsFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    const record = records.find((r: any) => r.id === assetId);
    if (!record) return null;
    return {
      ...record,
      values: JSON.parse(record.values || '{}'),
      createdAt: new Date(record.createdAt),
      updatedAt: new Date(record.updatedAt)
    };
  }

  async getAssetsByType(containerId: string, assetTypeId: string): Promise<IAsset[]> {
    const assetsFile = this.getAssetsFile(containerId);
    if (!fs.existsSync(assetsFile)) return [];

    const content = fs.readFileSync(assetsFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    return records
      .filter((r: any) => r.typeId === assetTypeId)
      .map((r: any) => ({
        ...r,
        values: JSON.parse(r.values || '{}'),
        createdAt: new Date(r.createdAt),
        updatedAt: new Date(r.updatedAt)
      }));
  }

  async updateAsset(containerId: string, assetId: string, updates: Partial<IAsset>): Promise<void> {
    const assetsFile = this.getAssetsFile(containerId);
    if (!fs.existsSync(assetsFile)) throw new Error('Asset not found');

    const content = fs.readFileSync(assetsFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    const index = records.findIndex((r: any) => r.id === assetId);
    if (index === -1) throw new Error('Asset not found');
    records[index] = {
      ...records[index],
      ...updates,
      values: JSON.stringify(updates.values || JSON.parse(records[index].values || '{}')),
      updatedAt: new Date().toISOString()
    };
    fs.writeFileSync(assetsFile, stringify(records, { header: true }));
  }

  async deleteAsset(containerId: string, assetId: string): Promise<void> {
    const assetsFile = this.getAssetsFile(containerId);
    if (!fs.existsSync(assetsFile)) return;

    const content = fs.readFileSync(assetsFile, 'utf-8');
    const records = parse(content, { columns: true, skip_empty_lines: true });
    const filteredRecords = records.filter((r: any) => r.id !== assetId);
    fs.writeFileSync(assetsFile, stringify(filteredRecords, { header: true }));
  }
} 