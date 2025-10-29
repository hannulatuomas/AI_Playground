import { BaseService } from './BaseService';
import { IContainer } from '../types/Container';
import { AxiosError } from 'axios';

export class ContainerService extends BaseService {
  private static instance: ContainerService;

  private constructor() {
    super();
  }

  public static getInstance(): ContainerService {
    if (!ContainerService.instance) {
      ContainerService.instance = new ContainerService();
    }
    return ContainerService.instance;
  }

  private convertToFrontendContainer(container: any): IContainer {
    return {
      ...container,
      createdAt: new Date(container.createdAt).toISOString(),
      updatedAt: new Date(container.updatedAt).toISOString(),
      assetTypeConfigs: container.assetTypeConfigs || [],
      assets: container.assets || []
    };
  }

  private convertToBackendContainer(container: Partial<IContainer>): any {
    const now = new Date().toISOString();
    return {
      id: container.id || crypto.randomUUID(),
      name: container.name?.trim() || '',
      description: container.description?.trim() || '',
      ownerId: container.ownerId,
      assetTypeConfigs: container.assetTypeConfigs?.map(type => ({
        id: type.id || crypto.randomUUID(),
        name: type.name?.trim() || '',
        label: type.label?.trim() || type.name?.trim() || '',
        fields: type.fields?.map(field => ({
          id: field.id || crypto.randomUUID(),
          name: field.name?.trim() || '',
          label: field.label?.trim() || field.name?.trim() || '',
          type: field.type,
          required: field.required || false,
          defaultValue: field.defaultValue,
          options: field.options,
          length: field.length,
          pattern: field.pattern,
          min: field.min,
          max: field.max,
          step: field.step,
          minDate: field.minDate,
          maxDate: field.maxDate,
          parentTypeId: field.parentTypeId,
          createdAt: field.createdAt || now,
          updatedAt: field.updatedAt || now
        })) || [],
        subtypes: type.subtypes?.map(subtype => ({
          id: subtype.id || crypto.randomUUID(),
          name: subtype.name?.trim() || '',
          label: subtype.label?.trim() || subtype.name?.trim() || '',
          parentTypeId: subtype.parentTypeId,
          fields: subtype.fields?.map(field => ({
            id: field.id || crypto.randomUUID(),
            name: field.name?.trim() || '',
            label: field.label?.trim() || field.name?.trim() || '',
            type: field.type,
            required: field.required || false,
            defaultValue: field.defaultValue,
            options: field.options,
            length: field.length,
            pattern: field.pattern,
            min: field.min,
            max: field.max,
            step: field.step,
            minDate: field.minDate,
            maxDate: field.maxDate,
            parentTypeId: field.parentTypeId,
            createdAt: field.createdAt || now,
            updatedAt: field.updatedAt || now
          })) || [],
          hiddenFields: subtype.hiddenFields || [],
          overriddenFields: subtype.overriddenFields || [],
          createdAt: subtype.createdAt || now,
          updatedAt: subtype.updatedAt || now
        })) || [],
        createdAt: type.createdAt || now,
        updatedAt: type.updatedAt || now
      })) || [],
      assets: container.assets || [],
      createdAt: container.createdAt || now,
      updatedAt: container.updatedAt || now
    };
  }

  private validateContainer(container: Partial<IContainer>): string[] {
    const errors: string[] = [];
    if (!container.name?.trim()) errors.push('Name is required');
    if (!container.ownerId) errors.push('Owner ID is required');
    if (!container.assetTypeConfigs?.length) errors.push('At least one asset type is required');
    
    // Validate asset types
    container.assetTypeConfigs?.forEach((type, index) => {
      if (!type.name?.trim()) errors.push(`Asset type ${index + 1}: Name is required`);
      if (!type.fields?.length) errors.push(`Asset type ${index + 1}: At least one field is required`);
      
      // Validate fields
      type.fields?.forEach((field, fieldIndex) => {
        if (!field.name?.trim()) errors.push(`Asset type ${index + 1}, Field ${fieldIndex + 1}: Name is required`);
        if (!field.type) errors.push(`Asset type ${index + 1}, Field ${fieldIndex + 1}: Type is required`);
      });
      
      // Validate subtypes
      type.subtypes?.forEach((subtype, subtypeIndex) => {
        if (!subtype.name?.trim()) errors.push(`Asset type ${index + 1}, Subtype ${subtypeIndex + 1}: Name is required`);
        
        // Validate subtype fields
        subtype.fields?.forEach((field, fieldIndex) => {
          if (!field.name?.trim()) errors.push(`Asset type ${index + 1}, Subtype ${subtypeIndex + 1}, Field ${fieldIndex + 1}: Name is required`);
          if (!field.type) errors.push(`Asset type ${index + 1}, Subtype ${subtypeIndex + 1}, Field ${fieldIndex + 1}: Type is required`);
        });
      });
    });
    
    return errors;
  }

  public async getContainers(): Promise<IContainer[]> {
    try {
      const response = await this.axiosInstance.get('/containers');
      const containers = this.handleResponse<any[]>(response);
      return containers.map(container => this.convertToFrontendContainer(container));
    } catch (error: unknown) {
      return this.handleError(error as AxiosError);
    }
  }

  public async getContainer(containerId: string): Promise<IContainer> {
    try {
      if (!containerId) {
        throw new Error('Container ID is required');
      }

      const response = await this.axiosInstance.get(`/containers/${containerId}`);
      const container = this.handleResponse<any>(response);
      return this.convertToFrontendContainer(container);
    } catch (error: unknown) {
      return this.handleError(error as AxiosError);
    }
  }

  public async createContainer(container: Omit<IContainer, 'id'>): Promise<IContainer> {
    try {
      const errors = this.validateContainer(container);
      if (errors.length > 0) {
        throw new Error(errors.join(', '));
      }

      const response = await this.axiosInstance.post(
        '/containers',
        this.convertToBackendContainer(container)
      );
      return this.convertToFrontendContainer(this.handleResponse<IContainer>(response));
    } catch (error: unknown) {
      return this.handleError(error as AxiosError);
    }
  }

  public async updateContainer(containerId: string, container: Partial<IContainer>): Promise<IContainer> {
    try {
      if (!containerId) {
        throw new Error('Container ID is required');
      }

      const errors = this.validateContainer(container);
      if (errors.length > 0) {
        throw new Error(errors.join(', '));
      }

      const response = await this.axiosInstance.put(
        `/containers/${containerId}`,
        this.convertToBackendContainer(container)
      );
      return this.convertToFrontendContainer(this.handleResponse<IContainer>(response));
    } catch (error: unknown) {
      return this.handleError(error as AxiosError);
    }
  }

  public async deleteContainer(containerId: string): Promise<void> {
    try {
      if (!containerId) {
        throw new Error('Container ID is required');
      }

      await this.axiosInstance.delete(`/containers/${containerId}`);
    } catch (error: unknown) {
      return this.handleError(error as AxiosError);
    }
  }

  public async getContainersByOwner(ownerId: string): Promise<IContainer[]> {
    try {
      if (!ownerId) {
        throw new Error('Owner ID is required');
      }

      const response = await this.axiosInstance.get(`/containers?ownerId=${ownerId}`);
      const containers = this.handleResponse<any[]>(response);
      return containers.map(container => this.convertToFrontendContainer(container));
    } catch (error: unknown) {
      return this.handleError(error as AxiosError);
    }
  }

  public async deleteAssetTypeConfig(containerId: string, typeId: string): Promise<void> {
    try {
      await this.axiosInstance.delete(`/containers/${containerId}/asset-types/${typeId}`);
    } catch (error) {
      return this.handleError(error as AxiosError);
    }
  }
} 