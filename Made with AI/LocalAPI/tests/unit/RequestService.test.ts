// Unit tests for RequestService with HTTP mocking
import nock from 'nock';
import { RequestService } from '../../src/main/services/RequestService';
import type { Request } from '../../src/types/models';

describe('RequestService', () => {
  let requestService: RequestService;

  beforeAll(() => {
    // Disable real HTTP requests
    nock.disableNetConnect();
  });

  afterAll(() => {
    // Re-enable real HTTP requests
    nock.enableNetConnect();
  });

  beforeEach(() => {
    requestService = new RequestService();
  });

  afterEach(() => {
    // Clean up all mocks after each test
    nock.cleanAll();
  });

  describe('Variable Resolution', () => {
    test('should resolve variables in URL', async () => {
      // Mock the HTTP request
      nock('https://api.example.com')
        .get('/users/123')
        .reply(200, { id: 123, name: 'John Doe' });

      const request: Request = {
        id: 'req1',
        name: 'Test',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com/users/{{userId}}',
        headers: [],
        queryParams: [],
        assertions: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const variables = { userId: '123' };

      const response = await requestService.sendRequest(request, variables);

      expect(response).toBeDefined();
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ id: 123, name: 'John Doe' });
    });

    test('should resolve variables in headers', async () => {
      // Mock the HTTP request with header matching
      nock('https://api.example.com', {
        reqheaders: {
          'authorization': 'Bearer abc123',
        },
      })
        .get('/data')
        .reply(200, { success: true });

      const request: Request = {
        id: 'req1',
        name: 'Test',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com/data',
        headers: [
          { key: 'Authorization', value: 'Bearer {{token}}', enabled: true },
        ],
        queryParams: [],
        assertions: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const variables = { token: 'abc123' };

      const response = await requestService.sendRequest(request, variables);

      expect(response).toBeDefined();
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ success: true });
    });
  });

  describe('Authentication', () => {
    test('should add Basic Auth header', async () => {
      // Mock the HTTP request with Basic Auth
      const basicAuth = Buffer.from('user:pass').toString('base64');
      nock('https://api.example.com', {
        reqheaders: {
          'authorization': `Basic ${basicAuth}`,
        },
      })
        .get('/secure')
        .reply(200, { authenticated: true });

      const request: Request = {
        id: 'req1',
        name: 'Test',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com/secure',
        headers: [],
        queryParams: [],
        auth: {
          type: 'basic',
          basic: {
            username: 'user',
            password: 'pass',
          },
        },
        assertions: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const response = await requestService.sendRequest(request, {});

      expect(response).toBeDefined();
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ authenticated: true });
    });

    test('should add Bearer token header', async () => {
      // Mock the HTTP request with Bearer token
      nock('https://api.example.com', {
        reqheaders: {
          'authorization': 'Bearer mytoken123',
        },
      })
        .get('/secure')
        .reply(200, { authenticated: true, user: 'testuser' });

      const request: Request = {
        id: 'req1',
        name: 'Test',
        protocol: 'REST',
        method: 'GET',
        url: 'https://api.example.com/secure',
        headers: [],
        queryParams: [],
        auth: {
          type: 'bearer',
          bearer: {
            token: 'mytoken123',
          },
        },
        assertions: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const response = await requestService.sendRequest(request, {});

      expect(response).toBeDefined();
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ authenticated: true, user: 'testuser' });
    });
  });

  describe('Request Body', () => {
    test('should parse JSON body', async () => {
      // Mock the HTTP POST request with body matching
      nock('https://api.example.com')
        .post('/users', {
          name: 'John',
          email: 'john@example.com',
        })
        .reply(201, {
          id: 1,
          name: 'John',
          email: 'john@example.com',
          created: true,
        });

      const request: Request = {
        id: 'req1',
        name: 'Test',
        protocol: 'REST',
        method: 'POST',
        url: 'https://api.example.com/users',
        headers: [
          { key: 'Content-Type', value: 'application/json', enabled: true },
        ],
        queryParams: [],
        body: {
          type: 'json',
          content: JSON.stringify({ name: 'John', email: 'john@example.com' }),
        },
        assertions: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const response = await requestService.sendRequest(request, {});

      expect(response).toBeDefined();
      expect(response.status).toBe(201);
      expect(response.body).toHaveProperty('id');
      expect(response.body).toHaveProperty('created', true);
    });
  });
});
