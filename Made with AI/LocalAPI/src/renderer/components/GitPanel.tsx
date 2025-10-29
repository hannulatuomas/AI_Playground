import React, { useState, useEffect, useCallback, useMemo } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Chip from '@mui/material/Chip';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import Checkbox from '@mui/material/Checkbox';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import Divider from '@mui/material/Divider';
import Tooltip from '@mui/material/Tooltip';
import GitHubIcon from '@mui/icons-material/GitHub';
import CommitIcon from '@mui/icons-material/Commit';
import RefreshIcon from '@mui/icons-material/Refresh';
import HistoryIcon from '@mui/icons-material/History';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import BranchIcon from '@mui/icons-material/AccountTree';

interface GitStatus {
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
}

interface GitCommit {
  hash: string;
  date: string;
  message: string;
  author: string;
}

const GitPanel: React.FC = React.memo(() => {
  const [isRepo, setIsRepo] = useState(false);
  const [status, setStatus] = useState<GitStatus | null>(null);
  const [commits, setCommits] = useState<GitCommit[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [commitDialogOpen, setCommitDialogOpen] = useState(false);
  const [commitMessage, setCommitMessage] = useState('');
  const [commitDescription, setCommitDescription] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [historyDialogOpen, setHistoryDialogOpen] = useState(false);

  // Load initial status
  useEffect(() => {
    checkRepository();
  }, []);

  const checkRepository = useCallback(async () => {
    try {
      const isGitRepo = await window.electronAPI.git.isRepository();
      setIsRepo(isGitRepo);
      
      if (isGitRepo) {
        await loadStatus();
      }
    } catch (err) {
      console.error('Failed to check repository:', err);
    }
  }, []);

  const loadStatus = useCallback(async () => {
    setLoading(true);
    setError('');
    
    try {
      const gitStatus = await window.electronAPI.git.getStatus();
      setStatus(gitStatus);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load status');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadHistory = useCallback(async () => {
    try {
      const log = await window.electronAPI.git.getLog(20);
      setCommits(log);
      setHistoryDialogOpen(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load history');
    }
  }, []);

  const handleInitRepo = useCallback(async () => {
    setLoading(true);
    setError('');
    
    try {
      await window.electronAPI.git.init();
      setIsRepo(true);
      await loadStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initialize repository');
    } finally {
      setLoading(false);
    }
  }, [loadStatus]);

  const handleStageFile = useCallback(async (file: string) => {
    try {
      await window.electronAPI.git.add([file]);
      await loadStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stage file');
    }
  }, [loadStatus]);

  const handleUnstageFile = useCallback(async (file: string) => {
    try {
      await window.electronAPI.git.reset([file]);
      await loadStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to unstage file');
    }
  }, [loadStatus]);

  const handleStageAll = useCallback(async () => {
    try {
      await window.electronAPI.git.add('.');
      await loadStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stage all files');
    }
  }, [loadStatus]);

  const handleOpenCommitDialog = useCallback(() => {
    setCommitMessage('');
    setCommitDescription('');
    setCommitDialogOpen(true);
  }, []);

  const handleCommit = useCallback(async () => {
    if (!commitMessage.trim()) {
      setError('Commit message is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await window.electronAPI.git.commit({
        message: commitMessage.trim(),
        description: commitDescription.trim() || undefined,
        addAll: false, // Files should already be staged
      });

      setCommitDialogOpen(false);
      setCommitMessage('');
      setCommitDescription('');
      await loadStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to commit');
    } finally {
      setLoading(false);
    }
  }, [commitMessage, commitDescription, loadStatus]);

  const allChanges = useMemo(() => {
    if (!status) return [];
    
    return [
      ...status.modified.map(f => ({ file: f, status: 'modified' as const })),
      ...status.created.map(f => ({ file: f, status: 'created' as const })),
      ...status.deleted.map(f => ({ file: f, status: 'deleted' as const })),
      ...status.renamed.map(f => ({ file: f, status: 'renamed' as const })),
    ];
  }, [status]);

  const stagedChanges = useMemo(() => {
    if (!status) return [];
    return status.staged.map(f => ({ file: f, status: 'staged' as const }));
  }, [status]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'modified': return 'warning';
      case 'created': return 'success';
      case 'deleted': return 'error';
      case 'renamed': return 'info';
      case 'staged': return 'primary';
      default: return 'default';
    }
  };

  if (!isRepo) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <GitHubIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          No Git Repository
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Initialize a Git repository to track changes to your collections
        </Typography>
        <Button
          variant="contained"
          startIcon={<GitHubIcon />}
          onClick={handleInitRepo}
          disabled={loading}
        >
          Initialize Repository
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <GitHubIcon />
          <Typography variant="h6">Git</Typography>
          {status && (
            <Chip
              icon={<BranchIcon />}
              label={status.branch}
              size="small"
              color="primary"
            />
          )}
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton size="small" onClick={loadStatus} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="History">
            <IconButton size="small" onClick={loadHistory}>
              <HistoryIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {loading && !status && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      )}

      {status && (
        <>
          {/* Status Summary */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Status
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {allChanges.length > 0 && (
                <Chip
                  label={`${allChanges.length} change${allChanges.length !== 1 ? 's' : ''}`}
                  size="small"
                  color="warning"
                />
              )}
              {stagedChanges.length > 0 && (
                <Chip
                  label={`${stagedChanges.length} staged`}
                  size="small"
                  color="primary"
                />
              )}
              {status.ahead > 0 && (
                <Chip
                  label={`${status.ahead} ahead`}
                  size="small"
                  color="info"
                />
              )}
              {status.behind > 0 && (
                <Chip
                  label={`${status.behind} behind`}
                  size="small"
                  color="default"
                />
              )}
              {allChanges.length === 0 && stagedChanges.length === 0 && (
                <Chip
                  label="No changes"
                  size="small"
                  color="success"
                />
              )}
            </Box>
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Staged Changes */}
          {stagedChanges.length > 0 && (
            <>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle2">
                  Staged Changes ({stagedChanges.length})
                </Typography>
                <Button
                  size="small"
                  variant="contained"
                  startIcon={<CommitIcon />}
                  onClick={handleOpenCommitDialog}
                  disabled={loading}
                >
                  Commit
                </Button>
              </Box>
              <List dense>
                {stagedChanges.map(({ file, status: fileStatus }) => (
                  <ListItem
                    key={file}
                    secondaryAction={
                      <IconButton
                        edge="end"
                        size="small"
                        onClick={() => handleUnstageFile(file)}
                      >
                        <RemoveIcon />
                      </IconButton>
                    }
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <Chip
                        label={fileStatus[0].toUpperCase()}
                        size="small"
                        color={getStatusColor(fileStatus) as any}
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={file}
                      primaryTypographyProps={{ variant: 'body2', fontFamily: 'monospace' }}
                    />
                  </ListItem>
                ))}
              </List>
              <Divider sx={{ my: 2 }} />
            </>
          )}

          {/* Unstaged Changes */}
          {allChanges.length > 0 && (
            <>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle2">
                  Changes ({allChanges.length})
                </Typography>
                <Button
                  size="small"
                  startIcon={<AddIcon />}
                  onClick={handleStageAll}
                  disabled={loading}
                >
                  Stage All
                </Button>
              </Box>
              <List dense>
                {allChanges.map(({ file, status: fileStatus }) => (
                  <ListItem
                    key={file}
                    secondaryAction={
                      <IconButton
                        edge="end"
                        size="small"
                        onClick={() => handleStageFile(file)}
                      >
                        <AddIcon />
                      </IconButton>
                    }
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <Chip
                        label={fileStatus[0].toUpperCase()}
                        size="small"
                        color={getStatusColor(fileStatus) as any}
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={file}
                      primaryTypographyProps={{ variant: 'body2', fontFamily: 'monospace' }}
                    />
                  </ListItem>
                ))}
              </List>
            </>
          )}
        </>
      )}

      {/* Commit Dialog */}
      <Dialog open={commitDialogOpen} onClose={() => setCommitDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Commit Changes</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="Commit Message"
            placeholder="Brief description of changes"
            value={commitMessage}
            onChange={(e) => setCommitMessage(e.target.value)}
            sx={{ mt: 1, mb: 2 }}
            required
          />
          <TextField
            fullWidth
            label="Description (optional)"
            placeholder="Detailed description of changes"
            value={commitDescription}
            onChange={(e) => setCommitDescription(e.target.value)}
            multiline
            rows={4}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCommitDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCommit}
            disabled={loading || !commitMessage.trim()}
            startIcon={loading ? <CircularProgress size={16} /> : <CommitIcon />}
          >
            Commit
          </Button>
        </DialogActions>
      </Dialog>

      {/* History Dialog */}
      <Dialog open={historyDialogOpen} onClose={() => setHistoryDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Commit History</DialogTitle>
        <DialogContent>
          <List>
            {commits.map((commit) => (
              <ListItem key={commit.hash} alignItems="flex-start">
                <ListItemText
                  primary={commit.message}
                  secondary={
                    <>
                      <Typography component="span" variant="body2" color="text.secondary">
                        {commit.author} • {new Date(commit.date).toLocaleString()}
                      </Typography>
                      <br />
                      <Typography component="span" variant="caption" fontFamily="monospace">
                        {commit.hash.substring(0, 7)}
                      </Typography>
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHistoryDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
});

GitPanel.displayName = 'GitPanel';

export default GitPanel;
