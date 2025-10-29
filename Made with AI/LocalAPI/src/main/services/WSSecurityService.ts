// WS-Security Service
// Provides WS-Security support for SOAP web services

import * as crypto from 'crypto';

export interface WSSecurityOptions {
  username?: string;
  password?: string;
  passwordType?: 'PasswordText' | 'PasswordDigest';
  nonce?: boolean;
  timestamp?: boolean;
  timestampTTL?: number; // Time to live in seconds
}

export interface SecurityHeader {
  username?: string;
  password?: string;
  passwordType?: string;
  nonce?: string;
  created?: string;
  expires?: string;
}

export class WSSecurityService {
  /**
   * Generate WS-Security header
   */
  generateSecurityHeader(options: WSSecurityOptions): string {
    const parts: string[] = [];

    parts.push('<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">');

    // Add timestamp if requested
    if (options.timestamp) {
      const timestamp = this.generateTimestamp(options.timestampTTL || 300);
      parts.push(timestamp);
    }

    // Add username token if credentials provided
    if (options.username && options.password) {
      const usernameToken = this.generateUsernameToken(options);
      parts.push(usernameToken);
    }

    parts.push('</wsse:Security>');

    return parts.join('\n');
  }

  /**
   * Generate timestamp element
   */
  private generateTimestamp(ttl: number): string {
    const now = new Date();
    const expires = new Date(now.getTime() + ttl * 1000);

    const created = now.toISOString();
    const expiresStr = expires.toISOString();

    return `  <wsu:Timestamp wsu:Id="Timestamp-${this.generateId()}">
    <wsu:Created>${created}</wsu:Created>
    <wsu:Expires>${expiresStr}</wsu:Expires>
  </wsu:Timestamp>`;
  }

  /**
   * Generate username token
   */
  private generateUsernameToken(options: WSSecurityOptions): string {
    const parts: string[] = [];
    const tokenId = this.generateId();

    parts.push(`  <wsse:UsernameToken wsu:Id="UsernameToken-${tokenId}">`);
    parts.push(`    <wsse:Username>${this.escapeXml(options.username!)}</wsse:Username>`);

    if (options.passwordType === 'PasswordDigest') {
      const nonce = this.generateNonce();
      const created = new Date().toISOString();
      const password = this.generatePasswordDigest(options.password!, nonce, created);

      parts.push(`    <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">${password}</wsse:Password>`);
      parts.push(`    <wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">${nonce}</wsse:Nonce>`);
      parts.push(`    <wsu:Created>${created}</wsu:Created>`);
    } else {
      // PasswordText (default)
      parts.push(`    <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">${this.escapeXml(options.password!)}</wsse:Password>`);
      
      if (options.nonce) {
        const nonce = this.generateNonce();
        parts.push(`    <wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">${nonce}</wsse:Nonce>`);
      }
    }

    parts.push('  </wsse:UsernameToken>');

    return parts.join('\n');
  }

  /**
   * Generate password digest
   */
  private generatePasswordDigest(password: string, nonce: string, created: string): string {
    const nonceBuffer = Buffer.from(nonce, 'base64');
    const createdBuffer = Buffer.from(created, 'utf8');
    const passwordBuffer = Buffer.from(password, 'utf8');

    const combined = Buffer.concat([nonceBuffer, createdBuffer, passwordBuffer]);
    const hash = crypto.createHash('sha1').update(combined).digest();

    return hash.toString('base64');
  }

  /**
   * Generate nonce
   */
  private generateNonce(): string {
    const nonce = crypto.randomBytes(16);
    return nonce.toString('base64');
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return crypto.randomBytes(8).toString('hex');
  }

  /**
   * Escape XML special characters
   */
  private escapeXml(str: string): string {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  }

  /**
   * Add WS-Security header to SOAP envelope
   */
  addSecurityToEnvelope(envelope: string, options: WSSecurityOptions): string {
    const securityHeader = this.generateSecurityHeader(options);

    // Find the SOAP Header section
    const headerMatch = envelope.match(/<soap:Header[^>]*>/i);
    
    if (headerMatch) {
      // Insert security into existing header
      const insertPos = headerMatch.index! + headerMatch[0].length;
      return envelope.slice(0, insertPos) + '\n' + securityHeader + envelope.slice(insertPos);
    } else {
      // Create new header section
      const bodyMatch = envelope.match(/<soap:Body/i);
      if (bodyMatch) {
        const headerSection = `  <soap:Header>\n${securityHeader}\n  </soap:Header>\n`;
        return envelope.slice(0, bodyMatch.index!) + headerSection + envelope.slice(bodyMatch.index!);
      }
    }

    return envelope;
  }

  /**
   * Create basic authentication header
   */
  createBasicAuth(username: string, password: string): string {
    const credentials = `${username}:${password}`;
    return `Basic ${Buffer.from(credentials).toString('base64')}`;
  }

  /**
   * Validate WS-Security header
   */
  validateSecurityHeader(header: SecurityHeader): { valid: boolean; errors?: string[] } {
    const errors: string[] = [];

    if (!header.username) {
      errors.push('Username is required');
    }

    if (!header.password) {
      errors.push('Password is required');
    }

    if (header.passwordType === 'PasswordDigest') {
      if (!header.nonce) {
        errors.push('Nonce is required for PasswordDigest');
      }
      if (!header.created) {
        errors.push('Created timestamp is required for PasswordDigest');
      }
    }

    return {
      valid: errors.length === 0,
      errors: errors.length > 0 ? errors : undefined,
    };
  }

  /**
   * Get security profiles
   */
  getSecurityProfiles(): Array<{ name: string; description: string; options: WSSecurityOptions }> {
    return [
      {
        name: 'Username Token (Text)',
        description: 'Username and password in plain text',
        options: {
          passwordType: 'PasswordText',
          timestamp: true,
        },
      },
      {
        name: 'Username Token (Digest)',
        description: 'Username with hashed password',
        options: {
          passwordType: 'PasswordDigest',
          nonce: true,
          timestamp: true,
        },
      },
      {
        name: 'Timestamp Only',
        description: 'Message timestamp for replay protection',
        options: {
          timestamp: true,
          timestampTTL: 300,
        },
      },
      {
        name: 'Full Security',
        description: 'Username token with digest, nonce, and timestamp',
        options: {
          passwordType: 'PasswordDigest',
          nonce: true,
          timestamp: true,
          timestampTTL: 300,
        },
      },
    ];
  }

  /**
   * Generate example SOAP request with WS-Security
   */
  generateExampleRequest(
    operation: string,
    namespace: string,
    args: Record<string, any>,
    security: WSSecurityOptions
  ): string {
    const argsXML = this.objectToXML(args, '      ');

    let envelope = `<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="${namespace}">
  <soap:Header>
  </soap:Header>
  <soap:Body>
    <tns:${operation}>
${argsXML}
    </tns:${operation}>
  </soap:Body>
</soap:Envelope>`;

    return this.addSecurityToEnvelope(envelope, security);
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
          lines.push(`${indent}<tns:${key}>${this.escapeXml(String(item))}</tns:${key}>`);
        }
      } else {
        lines.push(`${indent}<tns:${key}>${this.escapeXml(String(value))}</tns:${key}>`);
      }
    }

    return lines.join('\n');
  }
}

// Singleton instance
let wsSecurityServiceInstance: WSSecurityService | null = null;

export function getWSSecurityService(): WSSecurityService {
  if (!wsSecurityServiceInstance) {
    wsSecurityServiceInstance = new WSSecurityService();
  }
  return wsSecurityServiceInstance;
}
