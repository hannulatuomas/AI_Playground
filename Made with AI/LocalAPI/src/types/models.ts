// TypeScript type definitions for LocalAPI

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS';
export type RequestProtocol = 'REST' | 'GraphQL' | 'SOAP' | 'gRPC' | 'WebSocket' | 'SSE' | 'JMS' | 'MQTT';
export type AuthType = 'none' | 'basic' | 'bearer' | 'apikey' | 'oauth2' | 'digest';
export type VariableScope = 'global' | 'environment' | 'collection';

export interface Collection {
  id: string;
  name: string;
  description?: string;
  parentId?: string;
  requests: Request[];
  folders: Collection[];
  variables?: Variable[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Request {
  id: string;
  name: string;
  description?: string;
  collectionId?: string;
  protocol: RequestProtocol;
  method: HttpMethod;
  url: string;
  headers: Header[];
  queryParams: QueryParam[];
  body?: RequestBody;
  auth?: Auth;
  preRequestScript?: string;
  testScript?: string;
  assertions?: Assertion[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Header {
  key: string;
  value: string;
  enabled: boolean;
  description?: string;
}

export interface QueryParam {
  key: string;
  value: string;
  enabled: boolean;
  description?: string;
}

export interface RequestBody {
  type: 'none' | 'json' | 'xml' | 'form-data' | 'x-www-form-urlencoded' | 'raw' | 'binary' | 'graphql';
  content: string;
  formData?: FormDataItem[];
}

export interface FormDataItem {
  key: string;
  value: string;
  type: 'text' | 'file';
  enabled: boolean;
}

export interface Auth {
  type: AuthType;
  basic?: {
    username: string;
    password: string;
  };
  bearer?: {
    token: string;
  };
  apikey?: {
    key: string;
    value: string;
    addTo: 'header' | 'query';
  };
  oauth2?: {
    accessToken: string;
    tokenType?: string;
  };
  digest?: {
    username: string;
    password: string;
  };
}

export interface Response {
  status: number;
  statusText: string;
  headers: Record<string, string>;
  body: any;
  time: number;
  size: number;
  timestamp: Date;
}

export interface Environment {
  id: string;
  name: string;
  variables: Variable[];
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Variable {
  key: string;
  value: any;
  type: 'string' | 'number' | 'boolean' | 'secret';
  scope: VariableScope;
  enabled: boolean;
  description?: string;
}

export interface Assertion {
  id: string;
  type: 'status' | 'header' | 'body' | 'jsonpath' | 'xpath' | 'response-time' | 'custom';
  enabled: boolean;
  operator?: 'equals' | 'contains' | 'matches' | 'exists' | 'gt' | 'lt' | 'gte' | 'lte';
  expected?: any;
  actual?: any;
  path?: string;
  customScript?: string;
  result?: boolean;
  message?: string;
}

export interface TestResult {
  requestId: string;
  passed: boolean;
  assertions: AssertionResult[];
  response: Response;
  executionTime: number;
  timestamp: Date;
}

export interface AssertionResult {
  assertion: Assertion;
  passed: boolean;
  message: string;
}

export interface MockServer {
  id: string;
  name: string;
  port: number;
  collectionId: string;
  routes: MockRoute[];
  isRunning: boolean;
  createdAt: Date;
}

export interface MockRoute {
  path: string;
  method: HttpMethod;
  response: {
    status: number;
    headers: Record<string, string>;
    body: any;
    delay?: number;
  };
}

export interface Workflow {
  id: string;
  name: string;
  description?: string;
  requests: WorkflowRequest[];
  schedule?: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface WorkflowRequest {
  requestId: string;
  order: number;
  continueOnError: boolean;
  extractVariables?: VariableExtraction[];
}

export interface VariableExtraction {
  variableName: string;
  source: 'body' | 'header' | 'status';
  path?: string;
  pattern?: string;
}

export interface Settings {
  theme: 'light' | 'dark';
  requestTimeout: number;
  followRedirects: boolean;
  validateSSL: boolean;
  proxyEnabled: boolean;
  proxyUrl?: string;
  maxResponseSize: number;
  autoSave: boolean;
  autoSaveInterval?: number; // in seconds
  editorFontSize: number;
  editorTheme: string;
}

export interface Workspace {
  id: string;
  name: string;
  description?: string;
  collections: Collection[];
  environments: Environment[];
  globalVariables: Variable[];
  settings: Settings;
  createdAt: Date;
  updatedAt: Date;
  lastOpenedAt?: Date;
}

export interface WorkspaceSnapshot {
  id: string;
  workspaceId: string;
  name: string;
  description?: string;
  workspace: Workspace;
  createdAt: Date;
}

export interface WorkspaceTemplate {
  id: string;
  name: string;
  description?: string;
  workspace: Omit<Workspace, 'id' | 'createdAt' | 'updatedAt' | 'lastOpenedAt'>;
  tags?: string[];
  createdAt: Date;
  updatedAt: Date;
}

export interface WorkspaceMetadata {
  id: string;
  name: string;
  description?: string;
  path: string;
  lastOpenedAt: Date;
  createdAt: Date;
  updatedAt: Date;
}
