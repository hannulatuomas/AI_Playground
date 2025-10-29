import { BaseService } from './BaseService';
import { IUser } from '../types/User';
import { IdUtils } from '../utils/IdUtils';

export class UserService extends BaseService {
  private static instance: UserService;
  private currentUser: IUser | null = null;

  private constructor() {
    super('/api');
  }

  public static getInstance(): UserService {
    if (!UserService.instance) {
      UserService.instance = new UserService();
    }
    return UserService.instance;
  }

  public async login(username: string, password: string): Promise<IUser> {
    // TODO: Replace with actual API call
    // For now, return a debug user
    const debugUser: IUser = {
      id: IdUtils.generateUserId(),
      username: 'debug-user',
      email: 'debug@example.com',
      role: 'admin',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    this.currentUser = debugUser;
    return debugUser;
  }

  public async logout(): Promise<void> {
    this.currentUser = null;
  }

  public getCurrentUser(): IUser | null {
    return this.currentUser;
  }

  public isAuthenticated(): boolean {
    return this.currentUser !== null;
  }
} 