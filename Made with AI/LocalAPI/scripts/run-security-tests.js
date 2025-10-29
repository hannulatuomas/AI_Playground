#!/usr/bin/env node

/**
 * Security Test Runner
 * 
 * Runs comprehensive security tests with proper setup and reporting
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('╔════════════════════════════════════════════════════════════╗');
console.log('║  LocalAPI Security Test Suite                              ║');
console.log('╚════════════════════════════════════════════════════════════╝');
console.log('');

// Check if ZAP is configured
const zapConfigured = process.env.ZAP_API_KEY && process.env.ZAP_HOST && process.env.ZAP_PORT;

if (!zapConfigured) {
  console.log('⚠️  ZAP Configuration Missing');
  console.log('   Set environment variables for ZAP integration:');
  console.log('   - ZAP_API_KEY');
  console.log('   - ZAP_HOST (default: localhost)');
  console.log('   - ZAP_PORT (default: 8080)');
  console.log('');
  console.log('   ZAP tests will be skipped if ZAP is not running.');
  console.log('');
}

console.log('Running security tests...');
console.log('');

// Determine test pattern based on arguments
const args = process.argv.slice(2);
let testPattern = 'tests/**/*.test.ts';

if (args.includes('--e2e')) {
  testPattern = 'tests/e2e/**/*.test.ts';
  console.log('📋 Running E2E tests only');
} else if (args.includes('--unit')) {
  testPattern = 'tests/**/!(e2e)/*.test.ts';
  console.log('📋 Running unit tests only');
} else if (args.includes('--integration')) {
  testPattern = 'tests/integration/**/*.test.ts';
  console.log('📋 Running integration tests only');
} else {
  console.log('📋 Running all tests');
}

console.log('');

// Run Jest with the test pattern
const jest = spawn('npx', [
  'jest',
  testPattern,
  '--verbose',
  '--detectOpenHandles',
  '--forceExit',
  ...args.filter(arg => !['--e2e', '--unit', '--integration'].includes(arg))
], {
  stdio: 'inherit',
  shell: true,
});

jest.on('close', (code) => {
  console.log('');
  console.log('═══════════════════════════════════════════════════════════');
  
  if (code === 0) {
    console.log('✅ All tests passed!');
  } else {
    console.log('❌ Some tests failed. Exit code:', code);
  }
  
  console.log('═══════════════════════════════════════════════════════════');
  process.exit(code);
});

jest.on('error', (error) => {
  console.error('Failed to run tests:', error);
  process.exit(1);
});
