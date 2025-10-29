import { IAssetTypeConfig, IAssetSubTypeConfig } from '../types/FieldConfig';
import { FieldUtils } from './fieldUtils';

export class AssetTypeUtils {
  static convertToBackendAssetType(assetType: IAssetTypeConfig): any {
    return {
      name: assetType.name?.trim(),
      label: assetType.label?.trim(),
      fields: assetType.fields?.map(field => FieldUtils.convertToBackendField(field)) || [],
      subtypes: assetType.subtypes?.map(subType => AssetTypeUtils.convertToBackendSubType(subType)) || [],
      createdAt: assetType.createdAt || new Date().toISOString(),
      updatedAt: assetType.updatedAt || new Date().toISOString()
    };
  }

  static convertToFrontendAssetType(backendAssetType: any): IAssetTypeConfig {
    return {
      ...backendAssetType,
      createdAt: new Date(backendAssetType.createdAt).toISOString(),
      updatedAt: new Date(backendAssetType.updatedAt).toISOString(),
      fields: backendAssetType.fields?.map((field: any) => FieldUtils.convertToFrontendField(field)) || [],
      subtypes: backendAssetType.subtypes?.map((subType: any) => AssetTypeUtils.convertToFrontendSubType(subType)) || []
    };
  }

  static convertToBackendSubType(subType: IAssetSubTypeConfig): any {
    return {
      name: subType.name?.trim(),
      label: subType.label?.trim(),
      parentTypeId: subType.parentTypeId,
      fields: subType.fields?.map(field => FieldUtils.convertToBackendField(field)) || [],
      hiddenFields: subType.hiddenFields || [],
      overriddenFields: subType.overriddenFields || [],
      createdAt: subType.createdAt || new Date().toISOString(),
      updatedAt: subType.updatedAt || new Date().toISOString()
    };
  }

  static convertToFrontendSubType(backendSubType: any): IAssetSubTypeConfig {
    return {
      ...backendSubType,
      createdAt: new Date(backendSubType.createdAt).toISOString(),
      updatedAt: new Date(backendSubType.updatedAt).toISOString(),
      fields: backendSubType.fields?.map((field: any) => FieldUtils.convertToFrontendField(field)) || [],
      hiddenFields: backendSubType.hiddenFields || [],
      overriddenFields: backendSubType.overriddenFields || []
    };
  }
} 