# Phase 0.9.0 - API Specification Generation Implementation Plan

**Version:** 0.9.0  
**Feature:** Create API Specification from Requests  
**Status:** Planning  
**Date:** October 24, 2025

---

## Overview

Implementing reverse engineering and API specification generation from captured requests. This feature analyzes request/response patterns and automatically generates OpenAPI 3.0, AsyncAPI 2.x/3.x, and GraphQL schema specifications.

## TODO Tasks (12 items - ALL REQUIRED)

From TODO.md lines 248-259:

1. ✅ Request analyzer service (detect patterns)
2. ✅ Auto-generate OpenAPI 3.0 from requests
3. ✅ Auto-generate AsyncAPI from event requests
4. ✅ Auto-generate GraphQL schema from queries
5. ✅ Schema inference from request/response patterns
6. ✅ Automatic parameter detection
7. ✅ Response schema generation
8. ✅ API documentation generator
9. ✅ Schema validation and refinement UI
10. ✅ Export generated specs to files
11. ✅ Reverse engineering mode (capture traffic)
12. ✅ Schema merging (combine multiple requests)

---

## Architecture Design

### 1. Backend Service: RequestAnalyzerService

**File:** `src/main/services/RequestAnalyzerService.ts`  
**Estimated Lines:** ~600 lines

#### Responsibilities
- Analyze request/response patterns from console entries or collections
- Detect endpoints, methods, parameters
- Infer JSON schemas from request/response bodies
- Group related endpoints
- Detect authentication patterns
- Identify common headers and parameters

#### Key Methods
```typescript
class RequestAnalyzerService {
  // Analysis
  analyzeRequests(entries: ConsoleEntry[]): AnalysisResult
  analyzeCollection(collectionId: string): AnalysisResult
  detectEndpoints(entries: ConsoleEntry[]): Endpoint[]
  inferSchema(data: any): JSONSchema
  detectAuthPatterns(entries: ConsoleEntry[]): AuthPattern[]
  
  // Pattern detection
  groupByBasePath(endpoints: Endpoint[]): EndpointGroup[]
  detectPathParameters(urls: string[]): PathPattern
  detectQueryParameters(entries: ConsoleEntry[]): Parameter[]
  detectHeaders(entries: ConsoleEntry[]): Header[]
  
  // Schema inference
  inferRequestSchema(requests: any[]): JSONSchema
  inferResponseSchema(responses: any[]): JSONSchema
  mergeSchemas(schemas: JSONSchema[]): JSONSchema
  
  // Validation
  validateEndpoint(endpoint: Endpoint): ValidationResult
  refineSchema(schema: JSONSchema, userInput: any): JSONSchema
}
```

---

### 2. OpenAPI 3.0 Generator Service

**File:** `src/main/services/OpenAPIGeneratorService.ts`  
**Estimated Lines:** ~500 lines

#### Responsibilities
- Generate OpenAPI 3.0 specifications from analyzed requests
- Create paths, operations, parameters, request bodies, responses
- Generate component schemas
- Add examples from actual requests/responses
- Support OpenAPI extensions

#### Key Methods
```typescript
class OpenAPIGeneratorService {
  generateSpec(analysis: AnalysisResult, options: GeneratorOptions): OpenAPISpec
  createPathItem(endpoint: Endpoint): PathItem
  createOperation(endpoint: Endpoint): Operation
  createParameters(params: Parameter[]): ParameterObject[]
  createRequestBody(schema: JSONSchema): RequestBody
  createResponse(status: number, schema: JSONSchema): Response
  createSchemaComponent(name: string, schema: JSONSchema): Schema
  addExamples(spec: OpenAPISpec, entries: ConsoleEntry[]): OpenAPISpec
  validateSpec(spec: OpenAPISpec): ValidationResult
}
```

---

### 3. AsyncAPI Generator Service

**File:** `src/main/services/AsyncAPIGeneratorService.ts`  
**Estimated Lines:** ~400 lines

#### Responsibilities
- Generate AsyncAPI 2.x/3.x specifications
- Detect WebSocket and SSE patterns
- Create channels, operations, messages
- Support pub/sub patterns

#### Key Methods
```typescript
class AsyncAPIGeneratorService {
  generateSpec(analysis: AnalysisResult, options: GeneratorOptions): AsyncAPISpec
  detectChannels(entries: ConsoleEntry[]): Channel[]
  createChannel(pattern: MessagePattern): ChannelItem
  createMessage(schema: JSONSchema): Message
  detectProtocol(entries: ConsoleEntry[]): Protocol
}
```

---

### 4. GraphQL Schema Generator Service

**File:** `src/main/services/GraphQLSchemaGeneratorService.ts`  
**Estimated Lines:** ~350 lines

#### Responsibilities
- Generate GraphQL schema from GraphQL requests
- Detect queries, mutations, subscriptions
- Infer types from responses
- Create SDL (Schema Definition Language)

#### Key Methods
```typescript
class GraphQLSchemaGeneratorService {
  generateSchema(analysis: AnalysisResult): GraphQLSchema
  detectQueries(entries: ConsoleEntry[]): Query[]
  detectMutations(entries: ConsoleEntry[]): Mutation[]
  inferTypes(responses: any[]): GraphQLType[]
  generateSDL(schema: GraphQLSchema): string
}
```

---

### 5. UI Component: APISpecGenerator

**File:** `src/renderer/components/APISpecGenerator.tsx`  
**Estimated Lines:** ~700 lines

#### Features
- Source selection (console entries, collection, manual selection)
- Analysis preview with detected endpoints
- Spec type selection (OpenAPI, AsyncAPI, GraphQL)
- Schema refinement interface
- Live preview of generated spec
- Export options
- Validation and error display

#### Layout
```
┌────────────────────────────────────────────────────────────┐
│  API Specification Generator                                │
├────────────────────────────────────────────────────────────┤
│  [Step 1: Select Source]                                   │
│  ○ From Console (last 100 requests)                        │
│  ○ From Collection: [Collection Dropdown ▾]                │
│  ○ Manual Selection                                        │
│                                                             │
│  [Analyze] button                                          │
├────────────────────────────────────────────────────────────┤
│  [Step 2: Review Analysis]                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Detected Endpoints (12):                             │ │
│  │ ☑ GET /api/users                                     │ │
│  │ ☑ POST /api/users                                    │ │
│  │ ☑ GET /api/users/{id}                                │ │
│  │ ☑ PUT /api/users/{id}                                │ │
│  │ ...                                                   │ │
│  └──────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────┤
│  [Step 3: Configure Spec]                                  │
│  Spec Type: [OpenAPI 3.0 ▾]                               │
│  Title: [My API              ]                             │
│  Version: [1.0.0            ]                              │
│  Base URL: [https://api.example.com]                      │
│                                                             │
│  Options:                                                   │
│  ☑ Include examples from requests                          │
│  ☑ Include authentication                                  │
│  ☑ Include common headers                                  │
│  ☐ Group by tags                                           │
├────────────────────────────────────────────────────────────┤
│  [Step 4: Preview & Export]                                │
│  [Preview] [Validate] [Export ▾]                          │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ openapi: 3.0.0                                        │ │
│  │ info:                                                 │ │
│  │   title: My API                                       │ │
│  │   version: 1.0.0                                      │ │
│  │ paths:                                                │ │
│  │   /api/users:                                         │ │
│  │     get: ...                                          │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## Implementation Steps

### Step 1: RequestAnalyzerService (Phase 1)
- [ ] Create RequestAnalyzerService.ts
- [ ] Implement request pattern detection
- [ ] Implement endpoint grouping logic
- [ ] Implement schema inference from JSON data
- [ ] Implement parameter detection (path, query, header)
- [ ] Implement authentication pattern detection
- [ ] Write unit tests (25+ tests)

### Step 2: OpenAPI Generator (Phase 2)
- [ ] Create OpenAPIGeneratorService.ts
- [ ] Implement OpenAPI 3.0 spec generation
- [ ] Create path items and operations
- [ ] Generate component schemas
- [ ] Add examples from real requests
- [ ] Implement spec validation
- [ ] Write unit tests (20+ tests)

### Step 3: AsyncAPI Generator (Phase 3)
- [ ] Create AsyncAPIGeneratorService.ts
- [ ] Implement AsyncAPI 2.x/3.x generation
- [ ] Detect WebSocket/SSE patterns
- [ ] Create channels and messages
- [ ] Write unit tests (15+ tests)

### Step 4: GraphQL Generator (Phase 4)
- [ ] Create GraphQLSchemaGeneratorService.ts
- [ ] Implement GraphQL schema generation
- [ ] Detect queries, mutations, subscriptions
- [ ] Generate SDL
- [ ] Write unit tests (10+ tests)

### Step 5: UI Implementation (Phase 5)
- [ ] Create APISpecGenerator.tsx
- [ ] Implement source selection (console, collection, manual)
- [ ] Create analysis preview
- [ ] Implement spec configuration
- [ ] Add live preview panel
- [ ] Implement export functionality
- [ ] Add validation display

### Step 6: Integration (Phase 6)
- [ ] Add IPC handlers for all operations
- [ ] Update preload API
- [ ] Integrate with Console service
- [ ] Integrate with Collections
- [ ] Add navigation menu item

### Step 7: Testing (Phase 7)
- [ ] Integration tests (15+ tests)
- [ ] End-to-end tests (10+ tests)
- [ ] Performance tests
- [ ] Edge case testing

### Step 8: Documentation (Phase 8)
- [ ] Create API_SPEC_GENERATION_GUIDE.md
- [ ] Update README.md
- [ ] Update CHANGELOG.md
- [ ] Update TODO.md
- [ ] Update STATUS.md

---

## Data Models

### AnalysisResult
```typescript
interface AnalysisResult {
  endpoints: Endpoint[];
  schemas: Map<string, JSONSchema>;
  authentication: AuthPattern[];
  commonHeaders: Header[];
  basePaths: string[];
  metadata: {
    totalRequests: number;
    uniqueEndpoints: number;
    protocols: string[];
    analyzedAt: number;
  };
}
```

### Endpoint
```typescript
interface Endpoint {
  path: string;
  method: string;
  pathParameters: Parameter[];
  queryParameters: Parameter[];
  headers: Header[];
  requestBody?: {
    contentType: string;
    schema: JSONSchema;
    examples: any[];
  };
  responses: {
    [status: number]: {
      schema: JSONSchema;
      examples: any[];
    };
  };
  security?: SecurityRequirement[];
  tags?: string[];
  summary?: string;
  description?: string;
}
```

### JSONSchema
```typescript
interface JSONSchema {
  type: string;
  properties?: Record<string, JSONSchema>;
  items?: JSONSchema;
  required?: string[];
  enum?: any[];
  format?: string;
  example?: any;
  description?: string;
}
```

---

## OpenAPI 3.0 Generation Example

Input (Analyzed Requests):
```
GET /api/users?page=1&limit=10
Response: { users: [{id: 1, name: "John"}], total: 100 }

GET /api/users/1
Response: {id: 1, name: "John", email: "john@example.com"}

POST /api/users
Body: {name: "Jane", email: "jane@example.com"}
Response: {id: 2, name: "Jane", email: "jane@example.com"}
```

Output (OpenAPI Spec):
```yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
servers:
  - url: https://api.example.com
paths:
  /api/users:
    get:
      summary: List users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
        - name: limit
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  users:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  total:
                    type: integer
    post:
      summary: Create user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserInput'
      responses:
        '200':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
  /api/users/{id}:
    get:
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
          format: email
    UserInput:
      type: object
      required:
        - name
        - email
      properties:
        name:
          type: string
        email:
          type: string
          format: email
```

---

## Files to Create

### New Files (14 files)
1. `src/main/services/RequestAnalyzerService.ts` (~600 lines)
2. `src/main/services/OpenAPIGeneratorService.ts` (~500 lines)
3. `src/main/services/AsyncAPIGeneratorService.ts` (~400 lines)
4. `src/main/services/GraphQLSchemaGeneratorService.ts` (~350 lines)
5. `src/renderer/components/APISpecGenerator.tsx` (~700 lines)
6. `src/renderer/components/SchemaRefinementPanel.tsx` (~300 lines)
7. `src/renderer/components/EndpointSelector.tsx` (~250 lines)
8. `tests/unit/RequestAnalyzerService.test.ts` (~400 lines)
9. `tests/unit/OpenAPIGeneratorService.test.ts` (~350 lines)
10. `tests/unit/AsyncAPIGeneratorService.test.ts` (~250 lines)
11. `tests/unit/GraphQLSchemaGeneratorService.test.ts` (~200 lines)
12. `tests/integration/api-spec-generation.test.ts` (~400 lines)
13. `docs/API_SPEC_GENERATION_GUIDE.md` (~700 lines)
14. `commits/phase_0.9.0_api_spec_gen.bat`

### Files to Modify (5 files)
1. `src/main/ipc/handlers.ts` - Add spec generation IPC handlers
2. `src/preload/index.ts` - Add spec generation API
3. `src/renderer/App.tsx` - Add navigation menu item
4. `TODO.md` - Mark tasks complete
5. `CHANGELOG.md` - Add v0.9.0 entry

---

## Estimated Metrics

| Metric | Estimate |
|--------|----------|
| **Total Lines of Code** | ~4,500 lines |
| **New Services** | 4 (Analyzer, OpenAPI, AsyncAPI, GraphQL generators) |
| **New UI Components** | 3 components |
| **IPC Handlers** | 10 handlers |
| **Unit Tests** | 70+ tests |
| **Integration Tests** | 15+ tests |
| **E2E Tests** | 10+ tests |
| **Documentation** | 700+ lines |
| **Implementation Time** | Full implementation |

---

## Success Criteria

- ✅ All 12 TODO items implemented and working
- ✅ Request pattern analysis from console entries and collections
- ✅ OpenAPI 3.0 specification generation with examples
- ✅ AsyncAPI specification generation for event-driven APIs
- ✅ GraphQL schema generation from queries
- ✅ Schema inference from request/response data
- ✅ Automatic parameter detection (path, query, header)
- ✅ Response schema generation with status codes
- ✅ Schema validation and refinement UI
- ✅ Export to YAML and JSON files
- ✅ Reverse engineering mode from captured traffic
- ✅ Schema merging from multiple requests
- ✅ All tests passing (95+ tests)
- ✅ Complete documentation

---

## Next Steps After Completion

After API Specification Generation is 100% complete, move to next feature in order:
1. ✅ Debug Console (complete)
2. ✅ Create API Specification from Requests (current)
3. ⏳ API Publishing
4. ⏳ Settings & Configuration
5. ⏳ Tab System Redesign
6. ⏳ UI/UX Overhaul
7. ⏳ Testing & Documentation

---

**Status:** Ready to begin implementation  
**Next Action:** Create RequestAnalyzerService.ts
