import { CronMonitorService } from '../../src/main/services/CronMonitorService';

describe('CronMonitorService', () => {
  let service: CronMonitorService;

  beforeEach(() => {
    service = new CronMonitorService();
  });

  test('should create cron job', () => {
    const jobId = service.createJob({
      name: 'Test Job',
      schedule: '*/5 * * * *',
      requestId: 'req-1',
      requestName: 'Test Request',
      requestConfig: {
        method: 'GET',
        url: 'https://example.com/api',
      },
    });

    expect(jobId).toBeDefined();
  });

  test('should validate cron expression', () => {
    expect(service.validateCronExpression('* * * * *')).toBe(true);
    expect(service.validateCronExpression('invalid')).toBe(false);
  });

  test('should get all jobs', () => {
    service.createJob({
      name: 'Job 1',
      schedule: '* * * * *',
      requestId: 'req-1',
      requestName: 'Request 1',
      requestConfig: { method: 'GET', url: 'https://example.com' },
    });

    const jobs = service.getAllJobs();
    expect(jobs.length).toBeGreaterThan(0);
  });

  test('should delete job', () => {
    const jobId = service.createJob({
      name: 'Delete Test',
      schedule: '* * * * *',
      requestId: 'req-1',
      requestName: 'Request',
      requestConfig: { method: 'GET', url: 'https://example.com' },
    });

    const deleted = service.deleteJob(jobId);
    expect(deleted).toBe(true);
  });
});
