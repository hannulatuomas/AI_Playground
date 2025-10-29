import { MockServerService } from '../../src/main/services/MockServerService';

describe('MockServerService', () => {
  let service: MockServerService;

  beforeEach(() => {
    service = new MockServerService();
  });

  describe('Server Creation', () => {
    test('should create mock server', async () => {
      const serverId = await service.createServer({
        name: 'Test Server',
        port: 3001,
        routes: [
          {
            method: 'GET',
            path: '/test',
            response: {
              status: 200,
              body: { message: 'Hello' },
            },
          },
        ],
      });

      expect(serverId).toBeDefined();
      expect(typeof serverId).toBe('string');
    });

    test('should create server with multiple routes', async () => {
      const serverId = await service.createServer({
        name: 'Multi Route Server',
        port: 3002,
        routes: [
          {
            method: 'GET',
            path: '/users',
            response: { status: 200, body: [] },
          },
          {
            method: 'POST',
            path: '/users',
            response: { status: 201, body: { id: 1 } },
          },
        ],
      });

      const server = service.getServer(serverId);
      expect(server?.routes).toHaveLength(2);
    });
  });

  describe('Server Management', () => {
    test('should get server info', async () => {
      const serverId = await service.createServer({
        name: 'Info Test',
        port: 3003,
        routes: [],
      });

      const server = service.getServer(serverId);
      expect(server).toBeDefined();
      expect(server?.name).toBe('Info Test');
      expect(server?.port).toBe(3003);
    });

    test('should get all servers', async () => {
      await service.createServer({ name: 'Server 1', port: 3004, routes: [] });
      await service.createServer({ name: 'Server 2', port: 3005, routes: [] });

      const servers = service.getAllServers();
      expect(servers.length).toBeGreaterThanOrEqual(2);
    });

    test('should delete server', async () => {
      const serverId = await service.createServer({
        name: 'Delete Test',
        port: 3006,
        routes: [],
      });

      const deleted = await service.deleteServer(serverId);
      expect(deleted).toBe(true);

      const server = service.getServer(serverId);
      expect(server).toBeNull();
    });
  });

  describe('Route Management', () => {
    test('should add route to server', async () => {
      const serverId = await service.createServer({
        name: 'Route Test',
        port: 3007,
        routes: [],
      });

      const added = service.addRoute(serverId, {
        method: 'GET',
        path: '/new',
        response: { status: 200, body: 'New route' },
      });

      expect(added).toBe(true);
    });

    test('should remove route from server', async () => {
      const serverId = await service.createServer({
        name: 'Remove Route Test',
        port: 3008,
        routes: [
          {
            method: 'GET',
            path: '/remove',
            response: { status: 200, body: 'Remove me' },
          },
        ],
      });

      const removed = service.removeRoute(serverId, '/remove', 'GET');
      expect(removed).toBe(true);
    });
  });

  describe('Route Generation', () => {
    test('should generate routes from collection', () => {
      const collection = {
        name: 'Test Collection',
        children: [
          {
            type: 'request',
            id: '1',
            method: 'GET',
            url: 'http://localhost:3000/api/users',
            mockResponse: [{ id: 1, name: 'User' }],
          },
          {
            type: 'request',
            id: '2',
            method: 'POST',
            url: 'http://localhost:3000/api/users',
            mockResponse: { id: 2, name: 'New User' },
            mockDelay: 100,
          },
        ],
      };

      const routes = service.generateRoutesFromCollection(collection);
      expect(routes).toHaveLength(2);
      expect(routes[0].method).toBe('GET');
      expect(routes[0].path).toBe('/api/users');
      expect(routes[1].delay).toBe(100);
    });
  });

  describe('Port Availability', () => {
    test('should check port availability', () => {
      const available = service.isPortAvailable(9999);
      expect(available).toBe(true);
    });
  });
});
