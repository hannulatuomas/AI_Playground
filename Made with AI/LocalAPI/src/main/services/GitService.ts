// Git Service using simple-git
import simpleGit, { SimpleGit, StatusResult, LogResult, DiffResult } from 'simple-git';
import * as path from 'path';
import * as fs from 'fs';

export interface GitConfig {
  workingDir: string;
  userName?: string;
  userEmail?: string;
}

export interface GitStatus {
  isRepo: boolean;
  branch: string;
  modified: string[];
  created: string[];
  deleted: string[];
  renamed: string[];
  staged: string[];
  conflicted: string[];
  ahead: number;
  behind: number;
  tracking?: string;
}

export interface GitCommitInfo {
  hash: string;
  date: string;
  message: string;
  author: string;
  body?: string;
}

export interface GitCommitOptions {
  message: string;
  description?: string;
  files?: string[];
  addAll?: boolean;
}

export class GitService {
  private git: SimpleGit;
  private workingDir: string;

  constructor(config: GitConfig) {
    this.workingDir = config.workingDir;
    
    // Ensure directory exists before initializing git
    if (!fs.existsSync(this.workingDir)) {
      fs.mkdirSync(this.workingDir, { recursive: true });
    }
    
    this.git = simpleGit(this.workingDir);

    // Configure user if provided
    if (config.userName) {
      this.git.addConfig('user.name', config.userName);
    }
    if (config.userEmail) {
      this.git.addConfig('user.email', config.userEmail);
    }
  }

  /**
   * Check if directory is a git repository
   */
  async isRepository(): Promise<boolean> {
    try {
      await this.git.status();
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Initialize a new git repository
   */
  async init(): Promise<void> {
    try {
      await this.git.init();
      
      // Create .gitignore if it doesn't exist
      const gitignorePath = path.join(this.workingDir, '.gitignore');
      if (!fs.existsSync(gitignorePath)) {
        const defaultIgnore = [
          'node_modules/',
          'dist/',
          'release/',
          '.DS_Store',
          'Thumbs.db',
          '*.log',
          '.env',
          '.env.local',
          'data/*.db',
          'data/*.db-*',
        ].join('\n');
        
        fs.writeFileSync(gitignorePath, defaultIgnore);
      }
    } catch (error) {
      throw new Error(`Failed to initialize repository: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get repository status
   */
  async getStatus(): Promise<GitStatus> {
    try {
      const status: StatusResult = await this.git.status();
      
      return {
        isRepo: true,
        branch: status.current || 'main',
        modified: status.modified,
        created: status.created,
        deleted: status.deleted,
        renamed: status.renamed.map(r => `${r.from} -> ${r.to}`),
        staged: status.staged,
        conflicted: status.conflicted,
        ahead: status.ahead,
        behind: status.behind,
        tracking: status.tracking || undefined,
      };
    } catch (error) {
      throw new Error(`Failed to get status: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Stage files for commit
   */
  async add(files: string[] | string = '.'): Promise<void> {
    try {
      if (Array.isArray(files)) {
        await this.git.add(files);
      } else {
        await this.git.add(files);
      }
    } catch (error) {
      throw new Error(`Failed to stage files: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Unstage files
   */
  async reset(files?: string[]): Promise<void> {
    try {
      if (files && files.length > 0) {
        await this.git.reset(['HEAD', ...files]);
      } else {
        await this.git.reset(['HEAD']);
      }
    } catch (error) {
      throw new Error(`Failed to unstage files: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Commit staged changes
   */
  async commit(options: GitCommitOptions): Promise<string> {
    try {
      // Stage files if specified
      if (options.addAll) {
        await this.add('.');
      } else if (options.files && options.files.length > 0) {
        await this.add(options.files);
      }

      // Build commit message
      let message = options.message;
      if (options.description) {
        message += `\n\n${options.description}`;
      }

      // Commit
      const result = await this.git.commit(message);
      return result.commit;
    } catch (error) {
      throw new Error(`Failed to commit: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get commit history
   */
  async getLog(maxCount: number = 50): Promise<GitCommitInfo[]> {
    try {
      const log: LogResult = await this.git.log({ maxCount });
      
      return log.all.map(commit => ({
        hash: commit.hash,
        date: commit.date,
        message: commit.message,
        author: `${commit.author_name} <${commit.author_email}>`,
        body: commit.body || undefined,
      }));
    } catch (error) {
      throw new Error(`Failed to get log: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get diff for uncommitted changes
   */
  async getDiff(file?: string): Promise<string> {
    try {
      if (file) {
        const diff = await this.git.diff([file]);
        return diff;
      } else {
        const diff = await this.git.diff();
        return diff;
      }
    } catch (error) {
      throw new Error(`Failed to get diff: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get diff for staged changes
   */
  async getDiffStaged(file?: string): Promise<string> {
    try {
      if (file) {
        const diff = await this.git.diff(['--staged', file]);
        return diff;
      } else {
        const diff = await this.git.diff(['--staged']);
        return diff;
      }
    } catch (error) {
      throw new Error(`Failed to get staged diff: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Create a new branch
   */
  async createBranch(branchName: string, checkout: boolean = true): Promise<void> {
    try {
      if (checkout) {
        await this.git.checkoutLocalBranch(branchName);
      } else {
        await this.git.branch([branchName]);
      }
    } catch (error) {
      throw new Error(`Failed to create branch: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Switch to a branch
   */
  async checkout(branchName: string): Promise<void> {
    try {
      await this.git.checkout(branchName);
    } catch (error) {
      throw new Error(`Failed to checkout branch: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get list of branches
   */
  async getBranches(): Promise<{ current: string; all: string[] }> {
    try {
      const branches = await this.git.branch();
      return {
        current: branches.current,
        all: branches.all,
      };
    } catch (error) {
      throw new Error(`Failed to get branches: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Pull from remote
   */
  async pull(remote: string = 'origin', branch?: string): Promise<void> {
    try {
      if (branch) {
        await this.git.pull(remote, branch);
      } else {
        await this.git.pull();
      }
    } catch (error) {
      throw new Error(`Failed to pull: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Push to remote
   */
  async push(remote: string = 'origin', branch?: string): Promise<void> {
    try {
      if (branch) {
        await this.git.push(remote, branch);
      } else {
        await this.git.push();
      }
    } catch (error) {
      throw new Error(`Failed to push: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Add remote repository
   */
  async addRemote(name: string, url: string): Promise<void> {
    try {
      await this.git.addRemote(name, url);
    } catch (error) {
      throw new Error(`Failed to add remote: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get remote repositories
   */
  async getRemotes(): Promise<Array<{ name: string; refs: { fetch: string; push: string } }>> {
    try {
      const remotes = await this.git.getRemotes(true);
      return remotes;
    } catch (error) {
      throw new Error(`Failed to get remotes: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get current branch name
   */
  async getCurrentBranch(): Promise<string> {
    try {
      const branch = await this.git.branch();
      return branch.current;
    } catch (error) {
      throw new Error(`Failed to get current branch: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Check if there are uncommitted changes
   */
  async hasChanges(): Promise<boolean> {
    try {
      const status = await this.git.status();
      return !status.isClean();
    } catch (error) {
      return false;
    }
  }

  /**
   * Get file content at specific commit
   */
  async getFileAtCommit(commit: string, file: string): Promise<string> {
    try {
      const content = await this.git.show([`${commit}:${file}`]);
      return content;
    } catch (error) {
      throw new Error(`Failed to get file at commit: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Discard changes in working directory
   */
  async discardChanges(files?: string[]): Promise<void> {
    try {
      if (files && files.length > 0) {
        await this.git.checkout(files);
      } else {
        await this.git.checkout(['.']);
      }
    } catch (error) {
      throw new Error(`Failed to discard changes: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get git configuration
   */
  async getConfig(key: string): Promise<string | null> {
    try {
      const value = await this.git.getConfig(key);
      return value.value || null;
    } catch {
      return null;
    }
  }

  /**
   * Set git configuration
   */
  async setConfig(key: string, value: string): Promise<void> {
    try {
      await this.git.addConfig(key, value);
    } catch (error) {
      throw new Error(`Failed to set config: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
}

// Singleton instance
let gitServiceInstance: GitService | null = null;

export function getGitService(config?: GitConfig): GitService {
  if (!gitServiceInstance && config) {
    gitServiceInstance = new GitService(config);
  }
  if (!gitServiceInstance) {
    throw new Error('GitService not initialized. Provide config on first call.');
  }
  return gitServiceInstance;
}

export function initializeGitService(config: GitConfig): GitService {
  gitServiceInstance = new GitService(config);
  return gitServiceInstance;
}
