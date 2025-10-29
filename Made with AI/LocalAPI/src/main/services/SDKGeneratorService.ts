/**
 * SDKGeneratorService - Client SDK Code Generator
 * 
 * Generates client SDKs in multiple languages from OpenAPI specs
 * Supports: JavaScript/TypeScript, Python, Java, C#, Go, PHP
 */

import type { OpenAPISpec } from './OpenAPIGeneratorService';

export type SDKLanguage = 'javascript' | 'typescript' | 'python' | 'java' | 'csharp' | 'go' | 'php';

export interface SDKOptions {
  language: SDKLanguage;
  packageName?: string;
  className?: string;
  includeTests?: boolean;
  async?: boolean;
}

export interface GeneratedSDK {
  files: Map<string, string>;
  readme: string;
}

export class SDKGeneratorService {
  /**
   * Generate client SDK from OpenAPI spec
   */
  generateSDK(spec: OpenAPISpec, options: SDKOptions): GeneratedSDK {
    const files = new Map<string, string>();

    switch (options.language) {
      case 'javascript':
        return this.generateJavaScriptSDK(spec, options);
      case 'typescript':
        return this.generateTypeScriptSDK(spec, options);
      case 'python':
        return this.generatePythonSDK(spec, options);
      case 'java':
        return this.generateJavaSDK(spec, options);
      case 'csharp':
        return this.generateCSharpSDK(spec, options);
      case 'go':
        return this.generateGoSDK(spec, options);
      case 'php':
        return this.generatePHPSDK(spec, options);
      default:
        throw new Error(`Unsupported language: ${options.language}`);
    }
  }

  /**
   * Generate JavaScript SDK
   */
  private generateJavaScriptSDK(spec: OpenAPISpec, options: SDKOptions): GeneratedSDK {
    const files = new Map<string, string>();
    const className = options.className || this.toPascalCase(spec.info.title) + 'Client';

    const clientCode = `/**
 * ${spec.info.title} API Client
 * Version: ${spec.info.version}
 */

class ${className} {
  constructor(config = {}) {
    this.baseURL = config.baseURL || '${spec.servers?.[0]?.url || ''}';
    this.apiKey = config.apiKey;
    this.headers = config.headers || {};
  }

  async request(method, path, data = null) {
    const url = this.baseURL + path;
    const headers = {
      'Content-Type': 'application/json',
      ...this.headers,
    };

    if (this.apiKey) {
      headers['Authorization'] = \`Bearer \${this.apiKey}\`;
    }

    const options = {
      method,
      headers,
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    
    if (!response.ok) {
      throw new Error(\`HTTP error! status: \${response.status}\`);
    }

    return await response.json();
  }

${this.generateJavaScriptMethods(spec)}
}

module.exports = ${className};
`;

    files.set('index.js', clientCode);
    files.set('package.json', this.generatePackageJson(spec, options));

    return {
      files,
      readme: this.generateReadme(spec, options),
    };
  }

  /**
   * Generate TypeScript SDK
   */
  private generateTypeScriptSDK(spec: OpenAPISpec, options: SDKOptions): GeneratedSDK {
    const files = new Map<string, string>();
    const className = options.className || this.toPascalCase(spec.info.title) + 'Client';

    const clientCode = `/**
 * ${spec.info.title} API Client
 * Version: ${spec.info.version}
 */

export interface ClientConfig {
  baseURL?: string;
  apiKey?: string;
  headers?: Record<string, string>;
}

export class ${className} {
  private baseURL: string;
  private apiKey?: string;
  private headers: Record<string, string>;

  constructor(config: ClientConfig = {}) {
    this.baseURL = config.baseURL || '${spec.servers?.[0]?.url || ''}';
    this.apiKey = config.apiKey;
    this.headers = config.headers || {};
  }

  private async request<T>(method: string, path: string, data?: any): Promise<T> {
    const url = this.baseURL + path;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...this.headers,
    };

    if (this.apiKey) {
      headers['Authorization'] = \`Bearer \${this.apiKey}\`;
    }

    const options: RequestInit = {
      method,
      headers,
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    
    if (!response.ok) {
      throw new Error(\`HTTP error! status: \${response.status}\`);
    }

    return await response.json();
  }

${this.generateTypeScriptMethods(spec)}
}
`;

    files.set('index.ts', clientCode);
    files.set('package.json', this.generatePackageJson(spec, options));
    files.set('tsconfig.json', this.generateTsConfig());

    return {
      files,
      readme: this.generateReadme(spec, options),
    };
  }

  /**
   * Generate Python SDK
   */
  private generatePythonSDK(spec: OpenAPISpec, options: SDKOptions): GeneratedSDK {
    const files = new Map<string, string>();
    const className = options.className || this.toPascalCase(spec.info.title) + 'Client';

    const clientCode = `"""
${spec.info.title} API Client
Version: ${spec.info.version}
"""

import requests
from typing import Dict, Any, Optional

class ${className}:
    def __init__(self, base_url: str = "${spec.servers?.[0]?.url || ''}", api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def _request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        url = self.base_url + path
        response = self.session.request(method, url, json=data)
        response.raise_for_status()
        return response.json()

${this.generatePythonMethods(spec)}
`;

    files.set('client.py', clientCode);
    files.set('setup.py', this.generateSetupPy(spec, options));
    files.set('requirements.txt', 'requests>=2.28.0');

    return {
      files,
      readme: this.generateReadme(spec, options),
    };
  }

  /**
   * Generate Java SDK
   */
  private generateJavaSDK(spec: OpenAPISpec, options: SDKOptions): GeneratedSDK {
    const files = new Map<string, string>();
    const className = options.className || this.toPascalCase(spec.info.title) + 'Client';
    const packageName = options.packageName || 'com.api.client';

    const clientCode = `package ${packageName};

import java.net.http.*;
import java.net.URI;
import com.google.gson.Gson;

public class ${className} {
    private String baseURL;
    private String apiKey;
    private HttpClient client;
    private Gson gson;

    public ${className}(String baseURL, String apiKey) {
        this.baseURL = baseURL != null ? baseURL : "${spec.servers?.[0]?.url || ''}";
        this.apiKey = apiKey;
        this.client = HttpClient.newHttpClient();
        this.gson = new Gson();
    }

    private <T> T request(String method, String path, Object data, Class<T> responseType) throws Exception {
        HttpRequest.Builder builder = HttpRequest.newBuilder()
            .uri(URI.create(baseURL + path))
            .header("Content-Type", "application/json");

        if (apiKey != null) {
            builder.header("Authorization", "Bearer " + apiKey);
        }

        if (data != null) {
            String json = gson.toJson(data);
            builder.method(method, HttpRequest.BodyPublishers.ofString(json));
        } else {
            builder.method(method, HttpRequest.BodyPublishers.noBody());
        }

        HttpResponse<String> response = client.send(builder.build(), HttpResponse.BodyHandlers.ofString());
        return gson.fromJson(response.body(), responseType);
    }

${this.generateJavaMethods(spec)}
}
`;

    files.set(`${className}.java`, clientCode);
    files.set('pom.xml', this.generatePomXml(spec, options));

    return {
      files,
      readme: this.generateReadme(spec, options),
    };
  }

  /**
   * Generate C# SDK
   */
  private generateCSharpSDK(spec: OpenAPISpec, options: SDKOptions): GeneratedSDK {
    const files = new Map<string, string>();
    const className = options.className || this.toPascalCase(spec.info.title) + 'Client';

    const clientCode = `using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace ${options.packageName || 'ApiClient'}
{
    public class ${className}
    {
        private readonly HttpClient _httpClient;
        private readonly string _baseUrl;
        private readonly string _apiKey;

        public ${className}(string baseUrl = "${spec.servers?.[0]?.url || ''}", string apiKey = null)
        {
            _baseUrl = baseUrl;
            _apiKey = apiKey;
            _httpClient = new HttpClient();
            
            if (!string.IsNullOrEmpty(apiKey))
            {
                _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");
            }
        }

        private async Task<T> RequestAsync<T>(string method, string path, object data = null)
        {
            var url = _baseUrl + path;
            var request = new HttpRequestMessage(new HttpMethod(method), url);

            if (data != null)
            {
                var json = JsonSerializer.Serialize(data);
                request.Content = new StringContent(json, Encoding.UTF8, "application/json");
            }

            var response = await _httpClient.SendAsync(request);
            response.EnsureSuccessStatusCode();

            var responseContent = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<T>(responseContent);
        }

${this.generateCSharpMethods(spec)}
    }
}
`;

    files.set(`${className}.cs`, clientCode);
    files.set(`${className}.csproj`, this.generateCsProj(spec, options));

    return {
      files,
      readme: this.generateReadme(spec, options),
    };
  }

  /**
   * Generate Go SDK
   */
  private generateGoSDK(spec: OpenAPISpec, options: SDKOptions): GeneratedSDK {
    const files = new Map<string, string>();
    const packageName = options.packageName || 'apiclient';

    const clientCode = `package ${packageName}

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
)

type Client struct {
    BaseURL string
    APIKey  string
    client  *http.Client
}

func NewClient(baseURL, apiKey string) *Client {
    if baseURL == "" {
        baseURL = "${spec.servers?.[0]?.url || ''}"
    }
    return &Client{
        BaseURL: baseURL,
        APIKey:  apiKey,
        client:  &http.Client{},
    }
}

func (c *Client) request(method, path string, body interface{}, result interface{}) error {
    url := c.BaseURL + path
    
    var reqBody io.Reader
    if body != nil {
        jsonData, err := json.Marshal(body)
        if err != nil {
            return err
        }
        reqBody = bytes.NewBuffer(jsonData)
    }

    req, err := http.NewRequest(method, url, reqBody)
    if err != nil {
        return err
    }

    req.Header.Set("Content-Type", "application/json")
    if c.APIKey != "" {
        req.Header.Set("Authorization", "Bearer "+c.APIKey)
    }

    resp, err := c.client.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    if resp.StatusCode >= 400 {
        return fmt.Errorf("HTTP error: %d", resp.StatusCode)
    }

    return json.NewDecoder(resp.Body).Decode(result)
}

${this.generateGoMethods(spec)}
`;

    files.set('client.go', clientCode);
    files.set('go.mod', this.generateGoMod(spec, options));

    return {
      files,
      readme: this.generateReadme(spec, options),
    };
  }

  /**
   * Generate PHP SDK
   */
  private generatePHPSDK(spec: OpenAPISpec, options: SDKOptions): GeneratedSDK {
    const files = new Map<string, string>();
    const className = options.className || this.toPascalCase(spec.info.title) + 'Client';

    const clientCode = `<?php

namespace ${options.packageName || 'ApiClient'};

class ${className}
{
    private $baseURL;
    private $apiKey;

    public function __construct($baseURL = '${spec.servers?.[0]?.url || ''}', $apiKey = null)
    {
        $this->baseURL = $baseURL;
        $this->apiKey = $apiKey;
    }

    private function request($method, $path, $data = null)
    {
        $url = $this->baseURL . $path;
        
        $options = [
            'http' => [
                'method' => $method,
                'header' => "Content-Type: application/json\\r\\n",
            ]
        ];

        if ($this->apiKey) {
            $options['http']['header'] .= "Authorization: Bearer {$this->apiKey}\\r\\n";
        }

        if ($data) {
            $options['http']['content'] = json_encode($data);
        }

        $context = stream_context_create($options);
        $result = file_get_contents($url, false, $context);
        
        return json_decode($result, true);
    }

${this.generatePHPMethods(spec)}
}
`;

    files.set('Client.php', clientCode);
    files.set('composer.json', this.generateComposerJson(spec, options));

    return {
      files,
      readme: this.generateReadme(spec, options),
    };
  }

  // Helper methods for generating language-specific method implementations
  private generateJavaScriptMethods(spec: OpenAPISpec): string {
    const methods: string[] = [];

    for (const [path, pathItem] of Object.entries(spec.paths)) {
      for (const [method, operation] of Object.entries(pathItem)) {
        if (method === 'parameters') continue;
        const op = operation as any;
        const methodName = this.generateMethodName(method, path, op);
        const params = this.extractParameters(op);

        methods.push(`  async ${methodName}(${params.join(', ')}) {
    return await this.request('${method.toUpperCase()}', '${this.pathToTemplate(path)}'${params.includes('data') ? ', data' : ''});
  }`);
      }
    }

    return methods.join('\n\n');
  }

  private generateTypeScriptMethods(spec: OpenAPISpec): string {
    const methods: string[] = [];

    for (const [path, pathItem] of Object.entries(spec.paths)) {
      for (const [method, operation] of Object.entries(pathItem)) {
        if (method === 'parameters') continue;
        const op = operation as any;
        const methodName = this.generateMethodName(method, path, op);
        const params = this.extractParameters(op);

        methods.push(`  async ${methodName}(${params.join(', ')}): Promise<any> {
    return await this.request('${method.toUpperCase()}', '${this.pathToTemplate(path)}'${params.includes('data') ? ', data' : ''});
  }`);
      }
    }

    return methods.join('\n\n');
  }

  private generatePythonMethods(spec: OpenAPISpec): string {
    const methods: string[] = [];

    for (const [path, pathItem] of Object.entries(spec.paths)) {
      for (const [method, operation] of Object.entries(pathItem)) {
        if (method === 'parameters') continue;
        const op = operation as any;
        const methodName = this.toSnakeCase(this.generateMethodName(method, path, op));
        const params = this.extractParameters(op);

        methods.push(`    def ${methodName}(self${params.length > 0 ? ', ' + params.join(', ') : ''}):
        return self._request('${method.toUpperCase()}', '${this.pathToTemplate(path)}'${params.includes('data') ? ', data' : ''})`);
      }
    }

    return methods.join('\n\n');
  }

  private generateJavaMethods(spec: OpenAPISpec): string {
    const methods: string[] = [];

    for (const [path, pathItem] of Object.entries(spec.paths)) {
      for (const [method, operation] of Object.entries(pathItem)) {
        if (method === 'parameters') continue;
        const op = operation as any;
        const methodName = this.generateMethodName(method, path, op);

        methods.push(`    public Object ${methodName}() throws Exception {
        return request("${method.toUpperCase()}", "${this.pathToTemplate(path)}", null, Object.class);
    }`);
      }
    }

    return methods.join('\n\n');
  }

  private generateCSharpMethods(spec: OpenAPISpec): string {
    const methods: string[] = [];

    for (const [path, pathItem] of Object.entries(spec.paths)) {
      for (const [method, operation] of Object.entries(pathItem)) {
        if (method === 'parameters') continue;
        const op = operation as any;
        const methodName = this.toPascalCase(this.generateMethodName(method, path, op));

        methods.push(`        public async Task<object> ${methodName}Async()
        {
            return await RequestAsync<object>("${method.toUpperCase()}", "${this.pathToTemplate(path)}");
        }`);
      }
    }

    return methods.join('\n\n');
  }

  private generateGoMethods(spec: OpenAPISpec): string {
    const methods: string[] = [];

    for (const [path, pathItem] of Object.entries(spec.paths)) {
      for (const [method, operation] of Object.entries(pathItem)) {
        if (method === 'parameters') continue;
        const op = operation as any;
        const methodName = this.toPascalCase(this.generateMethodName(method, path, op));

        methods.push(`func (c *Client) ${methodName}() (interface{}, error) {
    var result interface{}
    err := c.request("${method.toUpperCase()}", "${this.pathToTemplate(path)}", nil, &result)
    return result, err
}`);
      }
    }

    return methods.join('\n\n');
  }

  private generatePHPMethods(spec: OpenAPISpec): string {
    const methods: string[] = [];

    for (const [path, pathItem] of Object.entries(spec.paths)) {
      for (const [method, operation] of Object.entries(pathItem)) {
        if (method === 'parameters') continue;
        const op = operation as any;
        const methodName = this.toCamelCase(this.generateMethodName(method, path, op));

        methods.push(`    public function ${methodName}()
    {
        return $this->request('${method.toUpperCase()}', '${this.pathToTemplate(path)}');
    }`);
      }
    }

    return methods.join('\n\n');
  }

  // Helper methods
  private generateMethodName(method: string, path: string, operation: any): string {
    if (operation.operationId) {
      return this.toCamelCase(operation.operationId);
    }

    const pathParts = path.split('/').filter(p => p && !p.startsWith('{'));
    const name = pathParts.join('_');
    return this.toCamelCase(`${method}_${name}`);
  }

  private extractParameters(operation: any): string[] {
    const params: string[] = [];

    if (operation.parameters) {
      for (const param of operation.parameters) {
        if (param.in === 'path') {
          params.push(param.name);
        }
      }
    }

    if (operation.requestBody) {
      params.push('data');
    }

    return params;
  }

  private pathToTemplate(path: string): string {
    return path.replace(/{([^}]+)}/g, '${$1}');
  }

  private toCamelCase(str: string): string {
    return str.replace(/[-_](.)/g, (_, c) => c.toUpperCase()).replace(/^(.)/, c => c.toLowerCase());
  }

  private toPascalCase(str: string): string {
    return str.replace(/[-_\s](.)/g, (_, c) => c.toUpperCase()).replace(/^(.)/, c => c.toUpperCase()).replace(/[^a-zA-Z0-9]/g, '');
  }

  private toSnakeCase(str: string): string {
    return str.replace(/[A-Z]/g, c => '_' + c.toLowerCase()).replace(/^_/, '');
  }

  // Configuration file generators
  private generatePackageJson(spec: OpenAPISpec, options: SDKOptions): string {
    return JSON.stringify({
      name: options.packageName || spec.info.title.toLowerCase().replace(/\s+/g, '-'),
      version: spec.info.version,
      description: spec.info.description,
      main: 'index.js',
      dependencies: {},
    }, null, 2);
  }

  private generateTsConfig(): string {
    return JSON.stringify({
      compilerOptions: {
        target: 'ES2020',
        module: 'commonjs',
        declaration: true,
        outDir: './dist',
        strict: true,
      },
      include: ['*.ts'],
    }, null, 2);
  }

  private generateSetupPy(spec: OpenAPISpec, options: SDKOptions): string {
    return `from setuptools import setup

setup(
    name='${options.packageName || spec.info.title.toLowerCase().replace(/\s+/g, '-')}',
    version='${spec.info.version}',
    description='${spec.info.description || ''}',
    py_modules=['client'],
    install_requires=['requests>=2.28.0'],
)`;
  }

  private generatePomXml(spec: OpenAPISpec, options: SDKOptions): string {
    return `<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>${options.packageName || 'com.api.client'}</groupId>
    <artifactId>${spec.info.title.toLowerCase().replace(/\s+/g, '-')}</artifactId>
    <version>${spec.info.version}</version>
    <dependencies>
        <dependency>
            <groupId>com.google.code.gson</groupId>
            <artifactId>gson</artifactId>
            <version>2.10.1</version>
        </dependency>
    </dependencies>
</project>`;
  }

  private generateCsProj(spec: OpenAPISpec, options: SDKOptions): string {
    return `<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
    <Version>${spec.info.version}</Version>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="System.Text.Json" Version="7.0.0" />
  </ItemGroup>
</Project>`;
  }

  private generateGoMod(spec: OpenAPISpec, options: SDKOptions): string {
    return `module ${options.packageName || 'apiclient'}

go 1.20`;
  }

  private generateComposerJson(spec: OpenAPISpec, options: SDKOptions): string {
    return JSON.stringify({
      name: options.packageName || spec.info.title.toLowerCase().replace(/\s+/g, '/'),
      version: spec.info.version,
      description: spec.info.description,
      require: {
        php: '>=7.4',
      },
    }, null, 2);
  }

  private generateReadme(spec: OpenAPISpec, options: SDKOptions): string {
    return `# ${spec.info.title} SDK

Version: ${spec.info.version}

## Installation

### ${options.language}

${this.getInstallationInstructions(options.language, options.packageName || spec.info.title)}

## Usage

\`\`\`${options.language}
${this.getUsageExample(options.language, spec)}
\`\`\`

## Documentation

For full API documentation, visit: ${spec.info.contact?.url || 'API documentation'}

## License

${spec.info.license?.name || 'MIT'}
`;
  }

  private getInstallationInstructions(language: string, packageName: string): string {
    const instructions: Record<string, string> = {
      javascript: `npm install ${packageName}`,
      typescript: `npm install ${packageName}`,
      python: `pip install ${packageName}`,
      java: 'Add to pom.xml dependencies',
      csharp: `dotnet add package ${packageName}`,
      go: `go get ${packageName}`,
      php: `composer require ${packageName}`,
    };
    return instructions[language] || '';
  }

  private getUsageExample(language: string, spec: OpenAPISpec): string {
    const className = this.toPascalCase(spec.info.title) + 'Client';
    
    const examples: Record<string, string> = {
      javascript: `const ${className} = require('${spec.info.title.toLowerCase()}');
const client = new ${className}({ apiKey: 'your-api-key' });`,
      typescript: `import { ${className} } from '${spec.info.title.toLowerCase()}';
const client = new ${className}({ apiKey: 'your-api-key' });`,
      python: `from client import ${className}
client = ${className}(api_key='your-api-key')`,
      java: `${className} client = new ${className}(null, "your-api-key");`,
      csharp: `var client = new ${className}(apiKey: "your-api-key");`,
      go: `client := NewClient("", "your-api-key")`,
      php: `$client = new ${className}(null, 'your-api-key');`,
    };
    
    return examples[language] || '';
  }
}
