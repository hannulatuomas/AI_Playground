import React from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Typography from '@mui/material/Typography';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import type { Auth, AuthType } from '../../../types/models';

interface AuthTabProps {
  auth?: Auth;
  onChange: (auth: Auth) => void;
}

const AuthTab: React.FC<AuthTabProps> = ({ auth, onChange }) => {
  const currentAuth = auth || { type: 'none' };

  const handleTypeChange = (type: AuthType) => {
    onChange({ type });
  };

  const handleBasicChange = (field: 'username' | 'password', value: string) => {
    onChange({
      ...currentAuth,
      basic: {
        username: field === 'username' ? value : currentAuth.basic?.username || '',
        password: field === 'password' ? value : currentAuth.basic?.password || '',
      },
    });
  };

  const handleBearerChange = (token: string) => {
    onChange({
      ...currentAuth,
      bearer: { token },
    });
  };

  const handleApiKeyChange = (field: 'key' | 'value' | 'addTo', value: string) => {
    onChange({
      ...currentAuth,
      apikey: {
        key: field === 'key' ? value : currentAuth.apikey?.key || '',
        value: field === 'value' ? value : currentAuth.apikey?.value || '',
        addTo: field === 'addTo' ? (value as 'header' | 'query') : currentAuth.apikey?.addTo || 'header',
      },
    });
  };

  return (
    <Box sx={{ p: 2 }}>
      <FormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel>Authentication Type</InputLabel>
        <Select
          value={currentAuth.type}
          label="Authentication Type"
          onChange={e => handleTypeChange(e.target.value as AuthType)}
        >
          <MenuItem value="none">No Auth</MenuItem>
          <MenuItem value="basic">Basic Auth</MenuItem>
          <MenuItem value="bearer">Bearer Token</MenuItem>
          <MenuItem value="apikey">API Key</MenuItem>
          <MenuItem value="oauth2">OAuth 2.0</MenuItem>
          <MenuItem value="digest">Digest Auth</MenuItem>
        </Select>
      </FormControl>

      {currentAuth.type === 'basic' && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Typography variant="subtitle2">Basic Authentication</Typography>
          <TextField
            fullWidth
            label="Username"
            value={currentAuth.basic?.username || ''}
            onChange={e => handleBasicChange('username', e.target.value)}
            placeholder="Enter username"
          />
          <TextField
            fullWidth
            label="Password"
            type="password"
            value={currentAuth.basic?.password || ''}
            onChange={e => handleBasicChange('password', e.target.value)}
            placeholder="Enter password"
          />
          <Typography variant="caption" color="text.secondary">
            Credentials will be base64 encoded and sent in Authorization header
          </Typography>
        </Box>
      )}

      {currentAuth.type === 'bearer' && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Typography variant="subtitle2">Bearer Token</Typography>
          <TextField
            fullWidth
            label="Token"
            value={currentAuth.bearer?.token || ''}
            onChange={e => handleBearerChange(e.target.value)}
            placeholder="Enter bearer token"
            multiline
            rows={3}
          />
          <Typography variant="caption" color="text.secondary">
            Token will be sent in Authorization header as: Bearer {'<token>'}
          </Typography>
        </Box>
      )}

      {currentAuth.type === 'apikey' && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Typography variant="subtitle2">API Key</Typography>
          <TextField
            fullWidth
            label="Key"
            value={currentAuth.apikey?.key || ''}
            onChange={e => handleApiKeyChange('key', e.target.value)}
            placeholder="e.g., X-API-Key"
          />
          <TextField
            fullWidth
            label="Value"
            value={currentAuth.apikey?.value || ''}
            onChange={e => handleApiKeyChange('value', e.target.value)}
            placeholder="Enter API key value"
          />
          <FormControl component="fieldset">
            <Typography variant="caption" sx={{ mb: 1 }}>
              Add to:
            </Typography>
            <RadioGroup
              row
              value={currentAuth.apikey?.addTo || 'header'}
              onChange={e => handleApiKeyChange('addTo', e.target.value)}
            >
              <FormControlLabel value="header" control={<Radio />} label="Header" />
              <FormControlLabel value="query" control={<Radio />} label="Query Params" />
            </RadioGroup>
          </FormControl>
        </Box>
      )}

      {currentAuth.type === 'oauth2' && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Typography variant="subtitle2">OAuth 2.0</Typography>
          <TextField
            fullWidth
            label="Access Token"
            value={currentAuth.oauth2?.accessToken || ''}
            onChange={e =>
              onChange({
                ...currentAuth,
                oauth2: { accessToken: e.target.value },
              })
            }
            placeholder="Enter access token"
            multiline
            rows={3}
          />
          <Typography variant="caption" color="text.secondary">
            OAuth 2.0 flow implementation coming soon
          </Typography>
        </Box>
      )}

      {currentAuth.type === 'digest' && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Typography variant="subtitle2">Digest Authentication</Typography>
          <TextField
            fullWidth
            label="Username"
            value={currentAuth.digest?.username || ''}
            onChange={e =>
              onChange({
                ...currentAuth,
                digest: {
                  username: e.target.value,
                  password: currentAuth.digest?.password || '',
                },
              })
            }
            placeholder="Enter username"
          />
          <TextField
            fullWidth
            label="Password"
            type="password"
            value={currentAuth.digest?.password || ''}
            onChange={e =>
              onChange({
                ...currentAuth,
                digest: {
                  username: currentAuth.digest?.username || '',
                  password: e.target.value,
                },
              })
            }
            placeholder="Enter password"
          />
        </Box>
      )}
    </Box>
  );
};

export default AuthTab;
