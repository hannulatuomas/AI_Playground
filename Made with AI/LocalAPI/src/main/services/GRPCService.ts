// gRPC Service
// Handles gRPC requests and proto file parsing/extraction

import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import * as fs from 'fs';
import * as path from 'path';

interface GRPCRequest {
  protoPath: string;
  packageName: string;
  serviceName: string;
  methodName: string;
  address: string;
  request: any;
  metadata?: Record<string, string>;
  deadline?: number;
}

interface GRPCResponse {
  response?: any;
  error?: string;
  metadata?: any;
  status?: any;
}

interface ProtoInfo {
  packages: PackageInfo[];
  services: ServiceInfo[];
  messages: MessageInfo[];
}

interface PackageInfo {
  name: string;
  services: string[];
}

interface ServiceInfo {
  name: string;
  package: string;
  methods: MethodInfo[];
}

interface MethodInfo {
  name: string;
  requestType: string;
  responseType: string;
  requestStream: boolean;
  responseStream: boolean;
  options?: any;
}

interface MessageInfo {
  name: string;
  package: string;
  fields: FieldInfo[];
}

interface FieldInfo {
  name: string;
  type: string;
  rule?: string;
  id: number;
  options?: any;
}

export class GRPCService {
  /**
   * Execute gRPC unary call
   */
  async executeUnaryCall(request: GRPCRequest): Promise<GRPCResponse> {
    try {
      // Load proto file
      const packageDefinition = await protoLoader.load(request.protoPath, {
        keepCase: true,
        longs: String,
        enums: String,
        defaults: true,
        oneofs: true,
      });

      const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);

      // Get the service
      const packageObj = this.getPackage(protoDescriptor, request.packageName);
      if (!packageObj) {
        throw new Error(`Package ${request.packageName} not found`);
      }

      const Service = (packageObj as any)[request.serviceName];
      if (!Service) {
        throw new Error(`Service ${request.serviceName} not found in package ${request.packageName}`);
      }

      // Create client
      const client = new Service(
        request.address,
        grpc.credentials.createInsecure()
      );

      // Prepare metadata
      const metadata = new grpc.Metadata();
      if (request.metadata) {
        for (const [key, value] of Object.entries(request.metadata)) {
          metadata.add(key, value);
        }
      }

      // Execute call
      return new Promise((resolve) => {
        const deadline = request.deadline
          ? Date.now() + request.deadline
          : Date.now() + 30000; // 30s default

        client[request.methodName](
          request.request,
          metadata,
          { deadline },
          (error: any, response: any) => {
            if (error) {
              resolve({
                error: error.message,
                status: error.code,
              });
            } else {
              resolve({
                response,
              });
            }
          }
        );
      });
    } catch (error: any) {
      return {
        error: error.message || 'gRPC call failed',
      };
    }
  }

  /**
   * Parse proto file and extract information
   */
  async parseProtoFile(protoPath: string): Promise<ProtoInfo> {
    try {
      // Load proto file
      const packageDefinition = await protoLoader.load(protoPath, {
        keepCase: true,
        longs: String,
        enums: String,
        defaults: true,
        oneofs: true,
        includeDirs: [path.dirname(protoPath)],
      });

      const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);

      const packages: PackageInfo[] = [];
      const services: ServiceInfo[] = [];
      const messages: MessageInfo[] = [];

      // Extract package and service information
      this.extractPackageInfo(protoDescriptor, '', packages, services);

      // Parse proto file content for messages
      const protoContent = fs.readFileSync(protoPath, 'utf-8');
      const parsedMessages = this.parseMessages(protoContent);
      messages.push(...parsedMessages);

      return {
        packages,
        services,
        messages,
      };
    } catch (error: any) {
      throw new Error(`Failed to parse proto file: ${error.message}`);
    }
  }

  /**
   * Extract package information recursively
   */
  private extractPackageInfo(
    obj: any,
    packagePath: string,
    packages: PackageInfo[],
    services: ServiceInfo[]
  ): void {
    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'object' && value !== null) {
        const currentPath = packagePath ? `${packagePath}.${key}` : key;

        // Check if it's a service
        if (this.isService(value)) {
          const methods = this.extractMethods(value);
          services.push({
            name: key,
            package: packagePath,
            methods,
          });

          // Add to package info
          const existingPackage = packages.find(p => p.name === packagePath);
          if (existingPackage) {
            existingPackage.services.push(key);
          } else {
            packages.push({
              name: packagePath || 'default',
              services: [key],
            });
          }
        } else {
          // Recursively search for services
          this.extractPackageInfo(value, currentPath, packages, services);
        }
      }
    }
  }

  /**
   * Check if object is a gRPC service
   */
  private isService(obj: any): boolean {
    return (
      typeof obj === 'function' &&
      obj.service &&
      typeof obj.service === 'object'
    );
  }

  /**
   * Extract methods from service
   */
  private extractMethods(service: any): MethodInfo[] {
    const methods: MethodInfo[] = [];

    if (service.service) {
      for (const [methodName, methodDef] of Object.entries(service.service)) {
        const def = methodDef as any;
        methods.push({
          name: methodName,
          requestType: def.requestType?.type?.name || 'Unknown',
          responseType: def.responseType?.type?.name || 'Unknown',
          requestStream: def.requestStream || false,
          responseStream: def.responseStream || false,
          options: def.options,
        });
      }
    }

    return methods;
  }

  /**
   * Parse messages from proto file content
   */
  private parseMessages(protoContent: string): MessageInfo[] {
    const messages: MessageInfo[] = [];
    const messageRegex = /message\s+(\w+)\s*\{([^}]+)\}/g;
    let match;

    while ((match = messageRegex.exec(protoContent)) !== null) {
      const messageName = match[1];
      const messageBody = match[2];

      const fields = this.parseFields(messageBody);

      messages.push({
        name: messageName,
        package: '', // Will be set by package context
        fields,
      });
    }

    return messages;
  }

  /**
   * Parse fields from message body
   */
  private parseFields(messageBody: string): FieldInfo[] {
    const fields: FieldInfo[] = [];
    const fieldRegex = /(repeated\s+)?(\w+)\s+(\w+)\s*=\s*(\d+);/g;
    let match;

    while ((match = fieldRegex.exec(messageBody)) !== null) {
      const rule = match[1] ? 'repeated' : undefined;
      const type = match[2];
      const name = match[3];
      const id = parseInt(match[4], 10);

      fields.push({
        name,
        type,
        rule,
        id,
      });
    }

    return fields;
  }

  /**
   * Get package from proto descriptor
   */
  private getPackage(protoDescriptor: any, packageName: string): any {
    if (!packageName) return protoDescriptor;

    const parts = packageName.split('.');
    let current = protoDescriptor;

    for (const part of parts) {
      current = current[part];
      if (!current) return null;
    }

    return current;
  }

  /**
   * Generate request template for method
   */
  generateRequestTemplate(method: MethodInfo, messages: MessageInfo[]): string {
    const requestMessage = messages.find(m => m.name === method.requestType);

    if (!requestMessage || requestMessage.fields.length === 0) {
      return '{}';
    }

    const fields: string[] = [];
    for (const field of requestMessage.fields) {
      const value = this.getExampleValue(field.type, field.rule);
      fields.push(`  "${field.name}": ${value}`);
    }

    return `{\n${fields.join(',\n')}\n}`;
  }

  /**
   * Get example value for field type
   */
  private getExampleValue(type: string, rule?: string): string {
    if (rule === 'repeated') {
      return '[]';
    }

    const lowerType = type.toLowerCase();

    if (lowerType === 'string') {
      return '""';
    }
    if (lowerType.includes('int') || lowerType.includes('float') || lowerType.includes('double')) {
      return '0';
    }
    if (lowerType === 'bool') {
      return 'false';
    }
    if (lowerType === 'bytes') {
      return '""';
    }

    // Complex type
    return '{}';
  }

  /**
   * Validate proto file
   */
  async validateProtoFile(protoPath: string): Promise<{ valid: boolean; error?: string }> {
    try {
      await protoLoader.load(protoPath, {
        keepCase: true,
        longs: String,
        enums: String,
        defaults: true,
        oneofs: true,
      });
      return { valid: true };
    } catch (error: any) {
      return {
        valid: false,
        error: error.message,
      };
    }
  }

  /**
   * Get proto file content
   */
  getProtoContent(protoPath: string): string {
    try {
      return fs.readFileSync(protoPath, 'utf-8');
    } catch (error: any) {
      throw new Error(`Failed to read proto file: ${error.message}`);
    }
  }

  /**
   * List available methods in service
   */
  async listMethods(protoPath: string, packageName: string, serviceName: string): Promise<string[]> {
    try {
      const protoInfo = await this.parseProtoFile(protoPath);
      const service = protoInfo.services.find(
        s => s.name === serviceName && s.package === packageName
      );

      if (!service) {
        throw new Error(`Service ${serviceName} not found`);
      }

      return service.methods.map(m => m.name);
    } catch (error: any) {
      throw new Error(`Failed to list methods: ${error.message}`);
    }
  }

  /**
   * Get method streaming type
   */
  getStreamingType(method: MethodInfo): string {
    if (method.requestStream && method.responseStream) {
      return 'Bidirectional Streaming';
    }
    if (method.requestStream) {
      return 'Client Streaming';
    }
    if (method.responseStream) {
      return 'Server Streaming';
    }
    return 'Unary';
  }
}

// Singleton instance
let grpcServiceInstance: GRPCService | null = null;

export function getGRPCService(): GRPCService {
  if (!grpcServiceInstance) {
    grpcServiceInstance = new GRPCService();
  }
  return grpcServiceInstance;
}
