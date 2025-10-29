import React from 'react';
import { Box, Typography, Divider, Link, Chip } from '@mui/material';
import MonacoEditor from '../MonacoEditor';

interface TestsTabProps {
  testScript: string;
  onTestScriptChange: (script: string) => void;
}

const TestsTab: React.FC<TestsTabProps> = ({
  testScript,
  onTestScriptChange,
}) => {
  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Test Script
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          Write tests to validate the response. Use <code>pm.test()</code> and <code>pm.expect()</code> 
          to create assertions.{' '}
          <Link href="#" onClick={(e) => { e.preventDefault(); /* Open docs */ }}>
            View documentation
          </Link>
        </Typography>
      </Box>

      <MonacoEditor
        value={testScript}
        onChange={onTestScriptChange}
        language="javascript"
        height="400px"
        placeholder="Write test script here (e.g., pm.test('Status code is 200', () => { pm.expect(pm.response.code).to.equal(200); }))"
      />

      <Divider sx={{ my: 2 }} />

      <Box>
        <Typography variant="subtitle2" gutterBottom>
          Common Test Snippets
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Box
            sx={{
              p: 1.5,
              bgcolor: 'background.paper',
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              cursor: 'pointer',
              '&:hover': { bgcolor: 'action.hover' },
            }}
            onClick={() => onTestScriptChange(
              `pm.test('Status code is 200', () => {\n  pm.expect(pm.response.code).to.equal(200);\n});\n\npm.test('Response time is acceptable', () => {\n  pm.expect(pm.response.responseTime).to.be.below(1000);\n});`
            )}
          >
            <Typography variant="body2" fontWeight={600}>
              Status code and response time
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Validate status is 200 and response time is under 1 second
            </Typography>
          </Box>

          <Box
            sx={{
              p: 1.5,
              bgcolor: 'background.paper',
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              cursor: 'pointer',
              '&:hover': { bgcolor: 'action.hover' },
            }}
            onClick={() => onTestScriptChange(
              `pm.test('Response is JSON', () => {\n  const jsonData = pm.response.json();\n  pm.expect(jsonData).to.be.an('object');\n});\n\npm.test('Has required fields', () => {\n  const jsonData = pm.response.json();\n  pm.expect(jsonData).to.have.property('id');\n  pm.expect(jsonData).to.have.property('name');\n});`
            )}
          >
            <Typography variant="body2" fontWeight={600}>
              JSON response validation
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Check response is JSON and has required properties
            </Typography>
          </Box>

          <Box
            sx={{
              p: 1.5,
              bgcolor: 'background.paper',
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              cursor: 'pointer',
              '&:hover': { bgcolor: 'action.hover' },
            }}
            onClick={() => onTestScriptChange(
              `pm.test('Extract and save data', () => {\n  const jsonData = pm.response.json();\n  \n  // Save values for next request\n  pm.variables.set('userId', jsonData.id);\n  pm.environment.set('authToken', jsonData.token);\n  \n  console.log('Saved userId:', jsonData.id);\n});`
            )}
          >
            <Typography variant="body2" fontWeight={600}>
              Extract data from response
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Save response values to variables for subsequent requests
            </Typography>
          </Box>

          <Box
            sx={{
              p: 1.5,
              bgcolor: 'background.paper',
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              cursor: 'pointer',
              '&:hover': { bgcolor: 'action.hover' },
            }}
            onClick={() => onTestScriptChange(
              `pm.test('Array validation', () => {\n  const jsonData = pm.response.json();\n  \n  pm.expect(jsonData).to.be.an('array');\n  pm.expect(jsonData).to.have.length.above(0);\n  \n  // Validate first item\n  const firstItem = jsonData[0];\n  pm.expect(firstItem).to.have.property('id');\n  pm.expect(firstItem.id).to.be.a('number');\n});`
            )}
          >
            <Typography variant="body2" fontWeight={600}>
              Array response validation
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Validate array structure and items
            </Typography>
          </Box>

          <Box
            sx={{
              p: 1.5,
              bgcolor: 'background.paper',
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              cursor: 'pointer',
              '&:hover': { bgcolor: 'action.hover' },
            }}
            onClick={() => onTestScriptChange(
              `pm.test('Header validation', () => {\n  pm.expect(pm.response.headers).to.have.property('content-type');\n  pm.expect(pm.response.headers['content-type']).to.include('application/json');\n});\n\npm.test('Status text is OK', () => {\n  pm.expect(pm.response.status).to.equal('OK');\n});`
            )}
          >
            <Typography variant="body2" fontWeight={600}>
              Header and status validation
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Check response headers and status text
            </Typography>
          </Box>

          <Box
            sx={{
              p: 1.5,
              bgcolor: 'background.paper',
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              cursor: 'pointer',
              '&:hover': { bgcolor: 'action.hover' },
            }}
            onClick={() => onTestScriptChange(
              `// Extract data using JSONPath\nconst userId = pm.extractJson('$.data.user.id', 'userId');\nconst email = pm.extractJson('$.data.user.email', 'userEmail');\n\npm.test('Extracted user data', () => {\n  pm.expect(userId).to.be.a('number');\n  pm.expect(email).to.be.a('string');\n  console.log('User ID:', userId);\n  console.log('Email:', email);\n});`
            )}
          >
            <Typography variant="body2" fontWeight={600}>
              JSONPath auto-extraction
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Extract nested values and save to variables
            </Typography>
          </Box>

          <Box
            sx={{
              p: 1.5,
              bgcolor: 'background.paper',
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              cursor: 'pointer',
              '&:hover': { bgcolor: 'action.hover' },
            }}
            onClick={() => onTestScriptChange(
              `// Query array with JSONPath\nconst jsonData = pm.response.json();\nconst activeUsers = pm.jsonPath(jsonData, '$.users[?(@.active==true)]');\nconst userEmails = pm.jsonPath(jsonData, '$.users[*].email');\n\npm.test('JSONPath queries', () => {\n  pm.expect(activeUsers).to.be.an('array');\n  pm.expect(userEmails).to.have.length.above(0);\n  console.log('Active users:', activeUsers.length);\n  console.log('Emails:', userEmails);\n});`
            )}
          >
            <Typography variant="body2" fontWeight={600}>
              JSONPath queries
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Query arrays and filter with JSONPath expressions
            </Typography>
          </Box>
        </Box>
      </Box>

      <Divider sx={{ my: 2 }} />

      <Box>
        <Typography variant="subtitle2" gutterBottom sx={{ mb: 1 }}>
          Available Assertions
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
          <Chip label="to.equal()" size="small" variant="outlined" />
          <Chip label="to.eql()" size="small" variant="outlined" />
          <Chip label="to.be.a()" size="small" variant="outlined" />
          <Chip label="to.have.property()" size="small" variant="outlined" />
          <Chip label="to.have.length()" size="small" variant="outlined" />
          <Chip label="to.include()" size="small" variant="outlined" />
          <Chip label="to.match()" size="small" variant="outlined" />
          <Chip label="to.be.above()" size="small" variant="outlined" />
          <Chip label="to.be.below()" size="small" variant="outlined" />
          <Chip label="to.be.true" size="small" variant="outlined" />
          <Chip label="to.be.false" size="small" variant="outlined" />
          <Chip label="to.be.null" size="small" variant="outlined" />
          <Chip label="not.to.*" size="small" variant="outlined" />
        </Box>
      </Box>
    </Box>
  );
};

export default TestsTab;
