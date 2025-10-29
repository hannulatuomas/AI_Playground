import { DataDrivenService } from '../../src/main/services/DataDrivenService';

describe('DataDrivenService', () => {
  let service: DataDrivenService;

  beforeEach(() => {
    service = new DataDrivenService();
  });

  test('should parse CSV data', async () => {
    const csv = 'name,email\nAlice,alice@test.com\nBob,bob@test.com';
    const dataSetId = await service.parseCSV(csv, 'Users');

    expect(dataSetId).toBeDefined();
    const dataSet = service.getDataSet(dataSetId);
    expect(dataSet?.rowCount).toBe(2);
  });

  test('should parse JSON data', async () => {
    const json = JSON.stringify([
      { name: 'Alice', email: 'alice@test.com' },
      { name: 'Bob', email: 'bob@test.com' },
    ]);
    const dataSetId = await service.parseJSON(json, 'Users');

    const dataSet = service.getDataSet(dataSetId);
    expect(dataSet?.rowCount).toBe(2);
  });

  test('should parse XML data', async () => {
    const xml = '<users><item><name>Alice</name></item><item><name>Bob</name></item></users>';
    const dataSetId = await service.parseXML(xml, 'Users');

    const dataSet = service.getDataSet(dataSetId);
    expect(dataSet?.rowCount).toBe(2);
  });

  test('should run data-driven test', async () => {
    const csv = 'name,email\nAlice,alice@test.com';
    const dataSetId = await service.parseCSV(csv, 'Users');

    const run = await service.runDataDriven({
      name: 'Test Run',
      dataSetId,
      requestTemplate: {
        method: 'POST',
        url: 'https://example.com/users',
        body: { name: '{{name}}', email: '{{email}}' },
      },
    });

    expect(run.totalIterations).toBe(1);
  });
});
