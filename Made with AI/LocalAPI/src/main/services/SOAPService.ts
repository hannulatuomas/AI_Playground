// SOAP Service
// Handles SOAP requests and WSDL parsing/extraction

import * as soap from 'soap';
import { XMLParser } from 'fast-xml-parser';
import { WSSecurityService, WSSecurityOptions } from './WSSecurityService';

interface SOAPRequest {
  wsdlUrl: string;
  method: string;
  args: Record<string, any>;
  headers?: Record<string, string>;
  endpoint?: string;
  wsSecurity?: WSSecurityOptions;
}

interface SOAPResponse {
  result?: any;
  error?: string;
  rawXML?: string;
}

interface WSDLInfo {
  services: ServiceInfo[];
  targetNamespace?: string;
  types: TypeInfo[];
}

interface ServiceInfo {
  name: string;
  ports: PortInfo[];
}

interface PortInfo {
  name: string;
  binding: string;
  address: string;
  operations: OperationInfo[];
}

interface OperationInfo {
  name: string;
  input?: MessageInfo;
  output?: MessageInfo;
  documentation?: string;
}

interface MessageInfo {
  name: string;
  parts: PartInfo[];
}

interface PartInfo {
  name: string;
  element?: string;
  type?: string;
}

interface TypeInfo {
  name: string;
  type: string;
  elements?: ElementInfo[];
}

interface ElementInfo {
  name: string;
  type: string;
  minOccurs?: string;
  maxOccurs?: string;
}

export class SOAPService {
  private wsSecurityService: WSSecurityService;

  constructor() {
    this.wsSecurityService = new WSSecurityService();
  }

  /**
   * Execute SOAP request
   */
  async executeRequest(request: SOAPRequest): Promise<SOAPResponse> {
    try {
      const client = await soap.createClientAsync(request.wsdlUrl, {
        endpoint: request.endpoint,
      });

      // Add WS-Security if provided
      if (request.wsSecurity) {
        this.addWSSecurity(client, request.wsSecurity);
      }

      // Set custom headers if provided
      if (request.headers) {
        for (const [key, value] of Object.entries(request.headers)) {
          client.addHttpHeader(key, value);
        }
      }

      // Execute the SOAP method
      const method = client[request.method];
      if (!method) {
        throw new Error(`Method ${request.method} not found in WSDL`);
      }

      const [result, rawResponse, soapHeader, rawRequest] = await method(request.args);

      return {
        result,
        rawXML: rawResponse,
      };
    } catch (error: any) {
      return {
        error: error.message || 'SOAP request failed',
      };
    }
  }

  /**
   * Parse WSDL and extract service information
   */
  async parseWSDL(wsdlUrl: string): Promise<WSDLInfo> {
    try {
      const client = await soap.createClientAsync(wsdlUrl);
      const description = client.describe();

      const services: ServiceInfo[] = [];
      const types: TypeInfo[] = [];

      // Parse services
      for (const [serviceName, service] of Object.entries(description)) {
        const ports: PortInfo[] = [];

        for (const [portName, port] of Object.entries(service as any)) {
          const operations: OperationInfo[] = [];

          for (const [operationName, operation] of Object.entries(port as any)) {
            const opInfo: OperationInfo = {
              name: operationName,
            };

            // Parse input
            if ((operation as any).input) {
              opInfo.input = {
                name: operationName + 'Request',
                parts: this.parseMessageParts((operation as any).input),
              };
            }

            // Parse output
            if ((operation as any).output) {
              opInfo.output = {
                name: operationName + 'Response',
                parts: this.parseMessageParts((operation as any).output),
              };
            }

            operations.push(opInfo);
          }

          ports.push({
            name: portName,
            binding: portName + 'Binding',
            address: (client.wsdl as any).services?.[serviceName]?.ports?.[portName]?.location || '',
            operations,
          });
        }

        services.push({
          name: serviceName,
          ports,
        });
      }

      return {
        services,
        targetNamespace: (client.wsdl as any).targetNamespace,
        types,
      };
    } catch (error: any) {
      throw new Error(`Failed to parse WSDL: ${error.message}`);
    }
  }

  /**
   * Parse message parts from operation
   */
  private parseMessageParts(message: any): PartInfo[] {
    const parts: PartInfo[] = [];

    if (typeof message === 'object') {
      for (const [key, value] of Object.entries(message)) {
        parts.push({
          name: key,
          type: this.getTypeName(value),
        });
      }
    }

    return parts;
  }

  /**
   * Get type name from value
   */
  private getTypeName(value: any): string {
    if (typeof value === 'string') {
      return value;
    }

    if (typeof value === 'object') {
      if (value.$type) {
        return value.$type;
      }
      if (value.targetNSAlias && value.targetName) {
        return `${value.targetNSAlias}:${value.targetName}`;
      }
      return 'object';
    }

    return 'string';
  }

  /**
   * Generate SOAP request template
   */
  generateRequestTemplate(operation: OperationInfo): string {
    const args: string[] = [];

    if (operation.input?.parts) {
      for (const part of operation.input.parts) {
        args.push(`  ${part.name}: ${this.getExampleValue(part.type || 'string')}`);
      }
    }

    return `{\n${args.join(',\n')}\n}`;
  }

  /**
   * Get example value for type
   */
  private getExampleValue(type: string): string {
    const lowerType = type.toLowerCase();

    if (lowerType.includes('string')) {
      return '""';
    }
    if (lowerType.includes('int') || lowerType.includes('number')) {
      return '0';
    }
    if (lowerType.includes('bool')) {
      return 'false';
    }
    if (lowerType.includes('date')) {
      return '"2024-01-01"';
    }
    if (lowerType.includes('array') || lowerType.includes('list')) {
      return '[]';
    }

    return '{}';
  }

  /**
   * Validate WSDL URL
   */
  async validateWSDL(wsdlUrl: string): Promise<{ valid: boolean; error?: string }> {
    try {
      await soap.createClientAsync(wsdlUrl);
      return { valid: true };
    } catch (error: any) {
      return {
        valid: false,
        error: error.message,
      };
    }
  }

  /**
   * Get WSDL as XML string
   */
  async getWSDLXML(wsdlUrl: string): Promise<string> {
    try {
      const response = await fetch(wsdlUrl);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.text();
    } catch (error: any) {
      throw new Error(`Failed to fetch WSDL: ${error.message}`);
    }
  }

  /**
   * Parse WSDL XML to extract types
   */
  async parseWSDLTypes(wsdlUrl: string): Promise<TypeInfo[]> {
    try {
      const wsdlXML = await this.getWSDLXML(wsdlUrl);
      const parser = new XMLParser({
        ignoreAttributes: false,
        attributeNamePrefix: '@_',
      });

      const parsed = parser.parse(wsdlXML);
      const types: TypeInfo[] = [];

      // Navigate to types section
      const definitions = parsed['wsdl:definitions'] || parsed.definitions;
      if (!definitions) return types;

      const typesSection = definitions['wsdl:types'] || definitions.types;
      if (!typesSection) return types;

      const schema = typesSection['xsd:schema'] || typesSection.schema;
      if (!schema) return types;

      // Parse complex types
      const complexTypes = schema['xsd:complexType'] || schema.complexType || [];
      const complexTypeArray = Array.isArray(complexTypes) ? complexTypes : [complexTypes];

      for (const complexType of complexTypeArray) {
        if (!complexType) continue;

        const typeName = complexType['@_name'];
        if (!typeName) continue;

        const elements: ElementInfo[] = [];
        const sequence = complexType['xsd:sequence'] || complexType.sequence;

        if (sequence) {
          const elementList = sequence['xsd:element'] || sequence.element || [];
          const elementArray = Array.isArray(elementList) ? elementList : [elementList];

          for (const element of elementArray) {
            if (!element) continue;

            elements.push({
              name: element['@_name'] || '',
              type: element['@_type'] || 'string',
              minOccurs: element['@_minOccurs'],
              maxOccurs: element['@_maxOccurs'],
            });
          }
        }

        types.push({
          name: typeName,
          type: 'complexType',
          elements,
        });
      }

      // Parse simple types
      const simpleTypes = schema['xsd:simpleType'] || schema.simpleType || [];
      const simpleTypeArray = Array.isArray(simpleTypes) ? simpleTypes : [simpleTypes];

      for (const simpleType of simpleTypeArray) {
        if (!simpleType) continue;

        const typeName = simpleType['@_name'];
        if (!typeName) continue;

        types.push({
          name: typeName,
          type: 'simpleType',
        });
      }

      return types;
    } catch (error: any) {
      throw new Error(`Failed to parse WSDL types: ${error.message}`);
    }
  }

  /**
   * Add WS-Security to SOAP client
   */
  private addWSSecurity(client: any, options: WSSecurityOptions): void {
    if (options.username && options.password) {
      // Create custom security header
      const securityHeader = this.wsSecurityService.generateSecurityHeader(options);
      
      // Add as SOAP header
      client.addSoapHeader(securityHeader, '', 'wsse', 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd');
    }
  }

  /**
   * Get WS-Security profiles
   */
  getSecurityProfiles() {
    return this.wsSecurityService.getSecurityProfiles();
  }

  /**
   * Generate SOAP envelope for request
   */
  generateSOAPEnvelope(
    operation: string,
    args: Record<string, any>,
    namespace: string = 'http://tempuri.org/',
    wsSecurity?: WSSecurityOptions
  ): string {
    if (wsSecurity) {
      return this.wsSecurityService.generateExampleRequest(operation, namespace, args, wsSecurity);
    }

    const argsXML = this.objectToXML(args, '    ');

    return `<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="${namespace}">
  <soap:Header/>
  <soap:Body>
    <tns:${operation}>
${argsXML}
    </tns:${operation}>
  </soap:Body>
</soap:Envelope>`;
  }

  /**
   * Convert object to XML
   */
  private objectToXML(obj: any, indent: string = ''): string {
    const lines: string[] = [];

    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'object' && !Array.isArray(value)) {
        lines.push(`${indent}<tns:${key}>`);
        lines.push(this.objectToXML(value, indent + '  '));
        lines.push(`${indent}</tns:${key}>`);
      } else if (Array.isArray(value)) {
        for (const item of value) {
          lines.push(`${indent}<tns:${key}>${item}</tns:${key}>`);
        }
      } else {
        lines.push(`${indent}<tns:${key}>${value}</tns:${key}>`);
      }
    }

    return lines.join('\n');
  }
}

// Singleton instance
let soapServiceInstance: SOAPService | null = null;

export function getSOAPService(): SOAPService {
  if (!soapServiceInstance) {
    soapServiceInstance = new SOAPService();
  }
  return soapServiceInstance;
}
