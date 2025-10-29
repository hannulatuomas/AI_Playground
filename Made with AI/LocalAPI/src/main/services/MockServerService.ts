// Mock Server Service
// Creates Express mock servers from collections

import express, { Express, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import { Server } from 'http';

interface MockServer {
  id: string;
  name: string;
  port: number;
  app: Express;
  server: Server | null;
  status: 'running' | 'stopped' | 'error';
  routes: MockRoute[];
  logs: MockLog[];
  createdAt: Date;
}

interface MockRoute {
  method: string;
  path: string;
  response: MockResponse;
  delay?: number;
  requestId?: string;
}

interface MockResponse {
  status: number;
  headers?: Record<string, string>;
  body: any;
}

interface MockLog {
  id: string;
  timestamp: Date;
  method: string;
  path: string;
  query: any;
  headers: any;
  body: any;
  response: {
    status: number;
    body: any;
  };
  duration: number;
}

interface CreateServerOptions {
  name: string;
  port: number;
  routes: MockRoute[];
  enableCors?: boolean;
  enableLogs?: boolean;
}

export class MockServerService {
  private servers: Map<string, MockServer> = new Map();

  /**
   * Create mock server from collection
   */
  async createServer(options: CreateServerOptions): Promise<string> {
    const serverId = this.generateId();

    const app = express();

    // Middleware
    if (options.enableCors !== false) {
      app.use(cors());
    }
    app.use(bodyParser.json());
    app.use(bodyParser.urlencoded({ extended: true }));
    app.use(bodyParser.text());
    app.use(bodyParser.raw());

    const mockServer: MockServer = {
      id: serverId,
      name: options.name,
      port: options.port,
      app,
      server: null,
      status: 'stopped',
      routes: options.routes,
      logs: [],
      createdAt: new Date(),
    };

    // Add logging middleware
    if (options.enableLogs !== false) {
      const self = this;
      app.use((req: Request, res: Response, next: NextFunction) => {
        const startTime = Date.now();
        const originalSend = res.send;

        res.send = function (this: Response, body: any): Response {
          const duration = Date.now() - startTime;
          
          mockServer.logs.push({
            id: self.generateId(),
            timestamp: new Date(),
            method: req.method,
            path: req.path,
            query: req.query,
            headers: req.headers,
            body: req.body,
            response: {
              status: res.statusCode,
              body,
            },
            duration,
          });

          // Limit logs to 1000 entries
          if (mockServer.logs.length > 1000) {
            mockServer.logs.shift();
          }

          return originalSend.call(this, body);
        };

        next();
      });
    }

    // Register routes
    for (const route of options.routes) {
      this.registerRoute(app, route);
    }

    // 404 handler
    app.use((req: Request, res: Response) => {
      res.status(404).json({
        error: 'Not Found',
        message: `Route ${req.method} ${req.path} not found`,
        availableRoutes: options.routes.map(r => `${r.method} ${r.path}`),
      });
    });

    this.servers.set(serverId, mockServer);

    return serverId;
  }

  /**
   * Register a route on the Express app
   */
  private registerRoute(app: Express, route: MockRoute): void {
    const method = route.method.toLowerCase();
    const handler = async (req: Request, res: Response) => {
      try {
        // Apply delay if specified
        if (route.delay) {
          await new Promise(resolve => setTimeout(resolve, route.delay));
        }

        // Set custom headers
        if (route.response.headers) {
          for (const [key, value] of Object.entries(route.response.headers)) {
            res.setHeader(key, value);
          }
        }

        // Send response
        res.status(route.response.status).send(route.response.body);
      } catch (error: any) {
        res.status(500).json({
          error: 'Internal Server Error',
          message: error.message,
        });
      }
    };

    // Register route based on method
    switch (method) {
      case 'get':
        app.get(route.path, handler);
        break;
      case 'post':
        app.post(route.path, handler);
        break;
      case 'put':
        app.put(route.path, handler);
        break;
      case 'patch':
        app.patch(route.path, handler);
        break;
      case 'delete':
        app.delete(route.path, handler);
        break;
      case 'options':
        app.options(route.path, handler);
        break;
      case 'head':
        app.head(route.path, handler);
        break;
      default:
        app.all(route.path, handler);
    }
  }

  /**
   * Start mock server
   */
  async startServer(serverId: string): Promise<boolean> {
    const mockServer = this.servers.get(serverId);

    if (!mockServer) {
      throw new Error('Server not found');
    }

    if (mockServer.status === 'running') {
      throw new Error('Server is already running');
    }

    return new Promise((resolve, reject) => {
      try {
        const server = mockServer.app.listen(mockServer.port, () => {
          mockServer.server = server;
          mockServer.status = 'running';
          resolve(true);
        });

        server.on('error', (error: any) => {
          mockServer.status = 'error';
          reject(error);
        });
      } catch (error) {
        mockServer.status = 'error';
        reject(error);
      }
    });
  }

  /**
   * Stop mock server
   */
  async stopServer(serverId: string): Promise<boolean> {
    const mockServer = this.servers.get(serverId);

    if (!mockServer) {
      throw new Error('Server not found');
    }

    if (!mockServer.server) {
      throw new Error('Server is not running');
    }

    return new Promise((resolve, reject) => {
      mockServer.server!.close((error) => {
        if (error) {
          reject(error);
        } else {
          mockServer.status = 'stopped';
          mockServer.server = null;
          resolve(true);
        }
      });
    });
  }

  /**
   * Add route to running server
   */
  addRoute(serverId: string, route: MockRoute): boolean {
    const mockServer = this.servers.get(serverId);

    if (!mockServer) {
      return false;
    }

    this.registerRoute(mockServer.app, route);
    mockServer.routes.push(route);

    return true;
  }

  /**
   * Remove route from server
   */
  removeRoute(serverId: string, routePath: string, method: string): boolean {
    const mockServer = this.servers.get(serverId);

    if (!mockServer) {
      return false;
    }

    const index = mockServer.routes.findIndex(
      r => r.path === routePath && r.method.toLowerCase() === method.toLowerCase()
    );

    if (index !== -1) {
      mockServer.routes.splice(index, 1);
      // Note: Express doesn't support removing routes dynamically
      // Server needs to be restarted for route removal to take effect
      return true;
    }

    return false;
  }

  /**
   * Get server info
   */
  getServer(serverId: string): MockServer | null {
    const server = this.servers.get(serverId);
    if (!server) return null;

    // Return without Express app (not serializable)
    return {
      ...server,
      app: null as any,
      server: null,
    };
  }

  /**
   * Get all servers
   */
  getAllServers(): Array<Omit<MockServer, 'app' | 'server'>> {
    return Array.from(this.servers.values()).map(server => ({
      id: server.id,
      name: server.name,
      port: server.port,
      status: server.status,
      routes: server.routes,
      logs: server.logs,
      createdAt: server.createdAt,
      app: null as any,
      server: null,
    }));
  }

  /**
   * Get server logs
   */
  getLogs(serverId: string, limit?: number): MockLog[] {
    const mockServer = this.servers.get(serverId);
    if (!mockServer) return [];

    if (limit) {
      return mockServer.logs.slice(-limit);
    }

    return mockServer.logs;
  }

  /**
   * Clear server logs
   */
  clearLogs(serverId: string): boolean {
    const mockServer = this.servers.get(serverId);
    if (mockServer) {
      mockServer.logs = [];
      return true;
    }
    return false;
  }

  /**
   * Delete server
   */
  async deleteServer(serverId: string): Promise<boolean> {
    const mockServer = this.servers.get(serverId);

    if (!mockServer) {
      return false;
    }

    // Stop server if running
    if (mockServer.status === 'running') {
      await this.stopServer(serverId);
    }

    this.servers.delete(serverId);
    return true;
  }

  /**
   * Generate routes from collection
   */
  generateRoutesFromCollection(collection: any): MockRoute[] {
    const routes: MockRoute[] = [];

    const processItem = (item: any) => {
      if (item.type === 'request') {
        // Extract path from URL
        const url = new URL(item.url || 'http://localhost/');
        const path = url.pathname;

        routes.push({
          method: item.method || 'GET',
          path,
          response: {
            status: 200,
            headers: {
              'Content-Type': 'application/json',
            },
            body: item.mockResponse || { message: 'Mock response' },
          },
          delay: item.mockDelay || 0,
          requestId: item.id,
        });
      } else if (item.type === 'folder' && item.children) {
        item.children.forEach(processItem);
      }
    };

    if (collection.children) {
      collection.children.forEach(processItem);
    }

    return routes;
  }

  /**
   * Get server statistics
   */
  getStatistics(serverId: string): {
    totalRequests: number;
    requestsByMethod: Record<string, number>;
    requestsByPath: Record<string, number>;
    averageResponseTime: number;
  } | null {
    const mockServer = this.servers.get(serverId);
    if (!mockServer) return null;

    const stats = {
      totalRequests: mockServer.logs.length,
      requestsByMethod: {} as Record<string, number>,
      requestsByPath: {} as Record<string, number>,
      averageResponseTime: 0,
    };

    let totalDuration = 0;

    for (const log of mockServer.logs) {
      // Count by method
      stats.requestsByMethod[log.method] = (stats.requestsByMethod[log.method] || 0) + 1;

      // Count by path
      stats.requestsByPath[log.path] = (stats.requestsByPath[log.path] || 0) + 1;

      // Sum duration
      totalDuration += log.duration;
    }

    if (mockServer.logs.length > 0) {
      stats.averageResponseTime = totalDuration / mockServer.logs.length;
    }

    return stats;
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Check if port is available
   */
  isPortAvailable(port: number): boolean {
    for (const server of this.servers.values()) {
      if (server.port === port && server.status === 'running') {
        return false;
      }
    }
    return true;
  }
}

// Singleton instance
let mockServerServiceInstance: MockServerService | null = null;

export function getMockServerService(): MockServerService {
  if (!mockServerServiceInstance) {
    mockServerServiceInstance = new MockServerService();
  }
  return mockServerServiceInstance;
}
