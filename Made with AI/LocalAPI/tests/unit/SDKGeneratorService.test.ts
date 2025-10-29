/**
 * SDKGeneratorService Unit Tests
 */

import { SDKGeneratorService } from '../../src/main/services/SDKGeneratorService';
import type { OpenAPISpec } from '../../src/main/services/OpenAPIGeneratorService';

describe('SDKGeneratorService', () => {
  let service: SDKGeneratorService;

  beforeEach(() => {
    service = new SDKGeneratorService();
  });

  const mockSpec: OpenAPISpec = {
    openapi: '3.0.0',
    info: {
      title: 'Test API',
      version: '1.0.0',
      description: 'Test API description',
    },
    servers: [{ url: 'https://api.example.com' }],
    paths: {
      '/users': {
        get: {
          operationId: 'getUsers',
          responses: {},
        },
        post: {
          operationId: 'createUser',
          requestBody: {
            content: {
              'application/json': {
                schema: { type: 'object' },
              },
            },
          },
          responses: {},
        },
      },
    },
  };

  describe('generateSDK', () => {
    it('should throw error for unsupported language', () => {
      expect(() => {
        service.generateSDK(mockSpec, { language: 'rust' as any });
      }).toThrow('Unsupported language: rust');
    });
  });

  describe('JavaScript SDK', () => {
    it('should generate JavaScript SDK', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'javascript' });

      expect(sdk.files.has('index.js')).toBe(true);
      expect(sdk.files.has('package.json')).toBe(true);
      expect(sdk.readme).toBeTruthy();
    });

    it('should include class definition', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'javascript' });
      const code = sdk.files.get('index.js')!;

      expect(code).toContain('class TestAPIClient');
      expect(code).toContain('constructor(config = {})');
      expect(code).toContain('async request(method, path, data = null)');
    });

    it('should include API methods', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'javascript' });
      const code = sdk.files.get('index.js')!;

      expect(code).toContain('async getUsers');
      expect(code).toContain('async createUser');
    });

    it('should include package.json', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'javascript' });
      const packageJson = JSON.parse(sdk.files.get('package.json')!);

      expect(packageJson.name).toBeTruthy();
      expect(packageJson.version).toBe('1.0.0');
      expect(packageJson.main).toBe('index.js');
    });
  });

  describe('TypeScript SDK', () => {
    it('should generate TypeScript SDK', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'typescript' });

      expect(sdk.files.has('index.ts')).toBe(true);
      expect(sdk.files.has('package.json')).toBe(true);
      expect(sdk.files.has('tsconfig.json')).toBe(true);
    });

    it('should include type definitions', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'typescript' });
      const code = sdk.files.get('index.ts')!;

      expect(code).toContain('export interface ClientConfig');
      expect(code).toContain('export class TestAPIClient');
      expect(code).toContain('Promise<');
    });

    it('should include tsconfig.json', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'typescript' });
      const tsconfig = JSON.parse(sdk.files.get('tsconfig.json')!);

      expect(tsconfig.compilerOptions).toBeDefined();
      expect(tsconfig.compilerOptions.target).toBeTruthy();
    });
  });

  describe('Python SDK', () => {
    it('should generate Python SDK', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'python' });

      expect(sdk.files.has('client.py')).toBe(true);
      expect(sdk.files.has('setup.py')).toBe(true);
      expect(sdk.files.has('requirements.txt')).toBe(true);
    });

    it('should include class definition', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'python' });
      const code = sdk.files.get('client.py')!;

      expect(code).toContain('class TestAPIClient');
      expect(code).toContain('def __init__');
      expect(code).toContain('def _request');
    });

    it('should include requirements.txt', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'python' });
      const requirements = sdk.files.get('requirements.txt')!;

      expect(requirements).toContain('requests');
    });
  });

  describe('Java SDK', () => {
    it('should generate Java SDK', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'java' });

      expect(sdk.files.has('TestAPIClient.java')).toBe(true);
      expect(sdk.files.has('pom.xml')).toBe(true);
    });

    it('should include package and imports', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'java', packageName: 'com.test.api' });
      const code = sdk.files.get('TestAPIClient.java')!;

      expect(code).toContain('package com.test.api');
      expect(code).toContain('import java.net.http');
      expect(code).toContain('import com.google.gson.Gson');
    });

    it('should include pom.xml with dependencies', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'java' });
      const pom = sdk.files.get('pom.xml')!;

      expect(pom).toContain('<project>');
      expect(pom).toContain('<groupId>');
      expect(pom).toContain('<artifactId>');
      expect(pom).toContain('gson');
    });
  });

  describe('C# SDK', () => {
    it('should generate C# SDK', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'csharp' });

      expect(sdk.files.has('TestAPIClient.cs')).toBe(true);
      expect(sdk.files.has('TestAPIClient.csproj')).toBe(true);
    });

    it('should include namespace and using statements', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'csharp', packageName: 'TestApi' });
      const code = sdk.files.get('TestAPIClient.cs')!;

      expect(code).toContain('namespace TestApi');
      expect(code).toContain('using System');
      expect(code).toContain('using System.Net.Http');
    });
  });

  describe('Go SDK', () => {
    it('should generate Go SDK', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'go' });

      expect(sdk.files.has('client.go')).toBe(true);
      expect(sdk.files.has('go.mod')).toBe(true);
    });

    it('should include package and imports', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'go', packageName: 'testapi' });
      const code = sdk.files.get('client.go')!;

      expect(code).toContain('package testapi');
      expect(code).toContain('import (');
      expect(code).toContain('encoding/json');
    });

    it('should include go.mod', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'go', packageName: 'testapi' });
      const goMod = sdk.files.get('go.mod')!;

      expect(goMod).toContain('module testapi');
      expect(goMod).toContain('go 1.20');
    });
  });

  describe('PHP SDK', () => {
    it('should generate PHP SDK', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'php' });

      expect(sdk.files.has('Client.php')).toBe(true);
      expect(sdk.files.has('composer.json')).toBe(true);
    });

    it('should include namespace and class', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'php', packageName: 'TestApi' });
      const code = sdk.files.get('Client.php')!;

      expect(code).toContain('<?php');
      expect(code).toContain('namespace TestApi');
      expect(code).toContain('class TestAPIClient');
    });

    it('should include composer.json', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'php' });
      const composer = JSON.parse(sdk.files.get('composer.json')!);

      expect(composer.name).toBeTruthy();
      expect(composer.require).toBeDefined();
      expect(composer.require.php).toBeTruthy();
    });
  });

  describe('README generation', () => {
    it('should generate README for all languages', () => {
      const languages: Array<'javascript' | 'typescript' | 'python' | 'java' | 'csharp' | 'go' | 'php'> = [
        'javascript', 'typescript', 'python', 'java', 'csharp', 'go', 'php'
      ];

      languages.forEach(language => {
        const sdk = service.generateSDK(mockSpec, { language });
        expect(sdk.readme).toBeTruthy();
        expect(sdk.readme).toContain('# Test API SDK');
        expect(sdk.readme).toContain('## Installation');
        expect(sdk.readme).toContain('## Usage');
      });
    });
  });

  describe('authentication support', () => {
    it('should include authentication in generated code', () => {
      const sdk = service.generateSDK(mockSpec, { language: 'javascript' });
      const code = sdk.files.get('index.js')!;

      expect(code).toContain('apiKey');
      expect(code).toContain('Authorization');
    });
  });

  describe('custom options', () => {
    it('should use custom package name', () => {
      const sdk = service.generateSDK(mockSpec, {
        language: 'javascript',
        packageName: 'my-custom-api-client',
      });
      const packageJson = JSON.parse(sdk.files.get('package.json')!);

      expect(packageJson.name).toBe('my-custom-api-client');
    });

    it('should use custom class name', () => {
      const sdk = service.generateSDK(mockSpec, {
        language: 'javascript',
        className: 'MyCustomClient',
      });
      const code = sdk.files.get('index.js')!;

      expect(code).toContain('class MyCustomClient');
    });
  });
});
