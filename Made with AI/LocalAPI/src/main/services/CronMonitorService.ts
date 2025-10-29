// Cron Monitor Service
// Schedules and monitors API requests with cron expressions

import * as cron from 'node-cron';

export interface CronJob {
  id: string;
  name: string;
  schedule: string; // Cron expression
  requestId: string;
  requestName: string;
  requestConfig: {
    method: string;
    url: string;
    headers?: Record<string, string>;
    body?: any;
  };
  enabled: boolean;
  lastRun?: Date;
  nextRun?: Date;
  runCount: number;
  successCount: number;
  failureCount: number;
  createdAt: Date;
  task?: cron.ScheduledTask;
}

export interface CronLog {
  id: string;
  jobId: string;
  jobName: string;
  timestamp: Date;
  status: 'success' | 'failure';
  response?: {
    status: number;
    statusText: string;
    time: number;
    body?: any;
  };
  error?: string;
}

export interface CronJobOptions {
  name: string;
  schedule: string;
  requestId: string;
  requestName: string;
  requestConfig: {
    method: string;
    url: string;
    headers?: Record<string, string>;
    body?: any;
  };
  enabled?: boolean;
}

export class CronMonitorService {
  private jobs: Map<string, CronJob> = new Map();
  private logs: Map<string, CronLog[]> = new Map();
  private maxLogsPerJob: number = 1000;

  /**
   * Create cron job
   */
  createJob(options: CronJobOptions): string {
    const jobId = this.generateId();

    // Validate cron expression
    if (!cron.validate(options.schedule)) {
      throw new Error('Invalid cron expression');
    }

    const job: CronJob = {
      id: jobId,
      name: options.name,
      schedule: options.schedule,
      requestId: options.requestId,
      requestName: options.requestName,
      requestConfig: options.requestConfig,
      enabled: options.enabled !== false,
      runCount: 0,
      successCount: 0,
      failureCount: 0,
      createdAt: new Date(),
    };

    this.jobs.set(jobId, job);
    this.logs.set(jobId, []);

    if (job.enabled) {
      this.startJob(jobId);
    }

    return jobId;
  }

  /**
   * Start cron job
   */
  startJob(jobId: string): boolean {
    const job = this.jobs.get(jobId);
    if (!job) return false;

    // Stop existing task if any
    if (job.task) {
      job.task.stop();
    }

    // Create new task
    const task = cron.schedule(job.schedule, async () => {
      await this.executeJob(jobId);
    });

    job.task = task;
    job.enabled = true;
    task.start();

    // Calculate next run time
    this.updateNextRunTime(job);

    return true;
  }

  /**
   * Stop cron job
   */
  stopJob(jobId: string): boolean {
    const job = this.jobs.get(jobId);
    if (!job || !job.task) return false;

    job.task.stop();
    job.enabled = false;
    job.nextRun = undefined;

    return true;
  }

  /**
   * Execute job immediately
   */
  async executeJobNow(jobId: string): Promise<boolean> {
    return await this.executeJob(jobId);
  }

  /**
   * Execute job
   */
  private async executeJob(jobId: string): Promise<boolean> {
    const job = this.jobs.get(jobId);
    if (!job) return false;

    const logEntry: CronLog = {
      id: this.generateId(),
      jobId,
      jobName: job.name,
      timestamp: new Date(),
      status: 'success',
    };

    try {
      // Execute request
      const response = await this.makeRequest(job.requestConfig);

      logEntry.response = response;
      logEntry.status = response.status >= 200 && response.status < 300 ? 'success' : 'failure';

      // Update job statistics
      job.runCount++;
      job.lastRun = new Date();
      
      if (logEntry.status === 'success') {
        job.successCount++;
      } else {
        job.failureCount++;
      }

      this.updateNextRunTime(job);
    } catch (error: any) {
      logEntry.status = 'failure';
      logEntry.error = error.message;
      job.runCount++;
      job.failureCount++;
      job.lastRun = new Date();
    }

    // Add log entry
    const jobLogs = this.logs.get(jobId) || [];
    jobLogs.push(logEntry);

    // Limit log size
    if (jobLogs.length > this.maxLogsPerJob) {
      jobLogs.shift();
    }

    this.logs.set(jobId, jobLogs);

    return logEntry.status === 'success';
  }

  /**
   * Make HTTP request (placeholder)
   */
  private async makeRequest(config: {
    method: string;
    url: string;
    headers?: Record<string, string>;
    body?: any;
  }): Promise<{
    status: number;
    statusText: string;
    time: number;
    body?: any;
  }> {
    // Placeholder - integrate with RequestService
    const startTime = Date.now();

    // Simulate request
    await new Promise(resolve => setTimeout(resolve, 100));

    return {
      status: 200,
      statusText: 'OK',
      time: Date.now() - startTime,
      body: { success: true },
    };
  }

  /**
   * Update next run time
   */
  private updateNextRunTime(job: CronJob): void {
    // This is a simplified calculation
    // In production, use a proper cron parser library
    job.nextRun = new Date(Date.now() + 60000); // Placeholder: 1 minute from now
  }

  /**
   * Get job
   */
  getJob(jobId: string): CronJob | null {
    const job = this.jobs.get(jobId);
    if (!job) return null;

    // Return without task (not serializable)
    return {
      ...job,
      task: undefined,
    };
  }

  /**
   * Get all jobs
   */
  getAllJobs(): CronJob[] {
    return Array.from(this.jobs.values()).map(job => ({
      ...job,
      task: undefined,
    }));
  }

  /**
   * Update job
   */
  updateJob(jobId: string, updates: Partial<CronJobOptions>): boolean {
    const job = this.jobs.get(jobId);
    if (!job) return false;

    // Update fields
    if (updates.name) job.name = updates.name;
    if (updates.schedule) {
      if (!cron.validate(updates.schedule)) {
        throw new Error('Invalid cron expression');
      }
      job.schedule = updates.schedule;
      
      // Restart job with new schedule
      if (job.enabled) {
        this.stopJob(jobId);
        this.startJob(jobId);
      }
    }
    if (updates.requestConfig) {
      job.requestConfig = updates.requestConfig;
    }

    return true;
  }

  /**
   * Delete job
   */
  deleteJob(jobId: string): boolean {
    const job = this.jobs.get(jobId);
    if (!job) return false;

    // Stop task if running
    if (job.task) {
      job.task.stop();
    }

    this.jobs.delete(jobId);
    this.logs.delete(jobId);

    return true;
  }

  /**
   * Get job logs
   */
  getJobLogs(jobId: string, limit?: number): CronLog[] {
    const logs = this.logs.get(jobId) || [];
    
    if (limit) {
      return logs.slice(-limit);
    }

    return logs;
  }

  /**
   * Get all logs
   */
  getAllLogs(limit?: number): CronLog[] {
    const allLogs: CronLog[] = [];

    for (const logs of this.logs.values()) {
      allLogs.push(...logs);
    }

    // Sort by timestamp descending
    allLogs.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

    if (limit) {
      return allLogs.slice(0, limit);
    }

    return allLogs;
  }

  /**
   * Clear job logs
   */
  clearJobLogs(jobId: string): boolean {
    if (this.logs.has(jobId)) {
      this.logs.set(jobId, []);
      return true;
    }
    return false;
  }

  /**
   * Get job statistics
   */
  getJobStatistics(jobId: string): {
    runCount: number;
    successCount: number;
    failureCount: number;
    successRate: number;
    lastRun?: Date;
    nextRun?: Date;
    averageResponseTime: number;
  } | null {
    const job = this.jobs.get(jobId);
    if (!job) return null;

    const logs = this.logs.get(jobId) || [];
    const totalTime = logs.reduce((sum, log) => sum + (log.response?.time || 0), 0);
    const averageResponseTime = logs.length > 0 ? totalTime / logs.length : 0;
    const successRate = job.runCount > 0 ? (job.successCount / job.runCount) * 100 : 0;

    return {
      runCount: job.runCount,
      successCount: job.successCount,
      failureCount: job.failureCount,
      successRate,
      lastRun: job.lastRun,
      nextRun: job.nextRun,
      averageResponseTime,
    };
  }

  /**
   * Get dashboard statistics
   */
  getDashboardStatistics(): {
    totalJobs: number;
    activeJobs: number;
    inactiveJobs: number;
    totalRuns: number;
    totalSuccesses: number;
    totalFailures: number;
    overallSuccessRate: number;
  } {
    const jobs = Array.from(this.jobs.values());

    const totalJobs = jobs.length;
    const activeJobs = jobs.filter(j => j.enabled).length;
    const inactiveJobs = jobs.filter(j => !j.enabled).length;
    const totalRuns = jobs.reduce((sum, j) => sum + j.runCount, 0);
    const totalSuccesses = jobs.reduce((sum, j) => sum + j.successCount, 0);
    const totalFailures = jobs.reduce((sum, j) => sum + j.failureCount, 0);
    const overallSuccessRate = totalRuns > 0 ? (totalSuccesses / totalRuns) * 100 : 0;

    return {
      totalJobs,
      activeJobs,
      inactiveJobs,
      totalRuns,
      totalSuccesses,
      totalFailures,
      overallSuccessRate,
    };
  }

  /**
   * Validate cron expression
   */
  validateCronExpression(expression: string): boolean {
    return cron.validate(expression);
  }

  /**
   * Get cron expression examples
   */
  getCronExamples(): Array<{ expression: string; description: string }> {
    return [
      { expression: '* * * * *', description: 'Every minute' },
      { expression: '*/5 * * * *', description: 'Every 5 minutes' },
      { expression: '0 * * * *', description: 'Every hour' },
      { expression: '0 */6 * * *', description: 'Every 6 hours' },
      { expression: '0 0 * * *', description: 'Daily at midnight' },
      { expression: '0 9 * * *', description: 'Daily at 9:00 AM' },
      { expression: '0 0 * * 0', description: 'Weekly on Sunday' },
      { expression: '0 0 1 * *', description: 'Monthly on the 1st' },
      { expression: '0 9 * * 1-5', description: 'Weekdays at 9:00 AM' },
    ];
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Singleton instance
let cronMonitorServiceInstance: CronMonitorService | null = null;

export function getCronMonitorService(): CronMonitorService {
  if (!cronMonitorServiceInstance) {
    cronMonitorServiceInstance = new CronMonitorService();
  }
  return cronMonitorServiceInstance;
}
