/**
 * NetworkTimeline Component - Network timing visualization
 * 
 * Displays visual timeline of request phases:
 * - DNS lookup
 * - TCP connection
 * - SSL handshake
 * - Request sending
 * - Response receiving
 * 
 * Features:
 * - Color-coded bars for each phase
 * - Tooltip with detailed timing breakdown
 * - Responsive width scaling
 * - Export timeline as image (future)
 */

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Tooltip,
} from '@mui/material';

interface TimingData {
  dns?: number;
  tcp?: number;
  ssl?: number;
  request?: number;
  response?: number;
  total: number;
}

interface NetworkTimelineProps {
  timings: TimingData;
  url?: string;
  method?: string;
}

const NetworkTimeline: React.FC<NetworkTimelineProps> = ({ timings, url, method }) => {
  const { dns = 0, tcp = 0, ssl = 0, request = 0, response = 0, total } = timings;

  // Calculate percentages for each phase
  const phases = [
    { name: 'DNS', duration: dns, color: '#4CAF50', start: 0 },
    { name: 'TCP', duration: tcp, color: '#2196F3', start: dns },
    { name: 'SSL', duration: ssl, color: '#9C27B0', start: dns + tcp },
    { name: 'Request', duration: request, color: '#FF9800', start: dns + tcp + ssl },
    { name: 'Response', duration: response, color: '#F44336', start: dns + tcp + ssl + request },
  ].filter(phase => phase.duration > 0);

  const getPhasePercentage = (duration: number): number => {
    return total > 0 ? (duration / total) * 100 : 0;
  };

  const getPhaseWidth = (duration: number): string => {
    const percentage = getPhasePercentage(duration);
    return `${percentage}%`;
  };

  const formatDuration = (ms: number): string => {
    return `${ms}ms`;
  };

  return (
    <Box>
      {url && (
        <Box sx={{ mb: 1 }}>
          <Typography variant="subtitle2">
            {method} {url}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Total: {formatDuration(total)}
          </Typography>
        </Box>
      )}

      {/* Timeline visualization */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          backgroundColor: 'grey.100',
          borderRadius: 1,
        }}
      >
        <Box
          sx={{
            display: 'flex',
            height: 40,
            width: '100%',
            backgroundColor: 'grey.200',
            borderRadius: 1,
            overflow: 'hidden',
            position: 'relative',
          }}
        >
          {phases.map((phase, index) => (
            <Tooltip
              key={index}
              title={
                <Box>
                  <Typography variant="caption" display="block">
                    <strong>{phase.name}</strong>
                  </Typography>
                  <Typography variant="caption" display="block">
                    Duration: {formatDuration(phase.duration)}
                  </Typography>
                  <Typography variant="caption" display="block">
                    Start: {formatDuration(phase.start)}
                  </Typography>
                  <Typography variant="caption" display="block">
                    End: {formatDuration(phase.start + phase.duration)}
                  </Typography>
                  <Typography variant="caption" display="block">
                    {getPhasePercentage(phase.duration).toFixed(1)}% of total
                  </Typography>
                </Box>
              }
              arrow
            >
              <Box
                sx={{
                  width: getPhaseWidth(phase.duration),
                  height: '100%',
                  backgroundColor: phase.color,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: 12,
                  fontWeight: 'bold',
                  borderRight: index < phases.length - 1 ? '1px solid white' : 'none',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': {
                    opacity: 0.8,
                  },
                }}
              >
                {getPhasePercentage(phase.duration) > 5 && phase.name}
              </Box>
            </Tooltip>
          ))}
        </Box>

        {/* Legend */}
        <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          {phases.map((phase, index) => (
            <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  backgroundColor: phase.color,
                  borderRadius: 0.5,
                }}
              />
              <Typography variant="caption">
                {phase.name}: {formatDuration(phase.duration)}
              </Typography>
            </Box>
          ))}
        </Box>

        {/* Timing breakdown table */}
        <Box sx={{ mt: 2 }}>
          <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 0.5 }}>
            Timing Breakdown:
          </Typography>
          {phases.map((phase, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: 11,
                py: 0.25,
              }}
            >
              <Typography variant="caption">{phase.name}</Typography>
              <Typography variant="caption" fontFamily="monospace">
                {formatDuration(phase.duration)} ({getPhasePercentage(phase.duration).toFixed(1)}%)
              </Typography>
            </Box>
          ))}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              fontSize: 11,
              py: 0.25,
              borderTop: 1,
              borderColor: 'divider',
              mt: 0.5,
              pt: 0.5,
            }}
          >
            <Typography variant="caption" fontWeight="bold">Total</Typography>
            <Typography variant="caption" fontFamily="monospace" fontWeight="bold">
              {formatDuration(total)}
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* Time scale */}
      <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between', px: 2 }}>
        <Typography variant="caption" color="text.secondary">0ms</Typography>
        <Typography variant="caption" color="text.secondary">
          {formatDuration(total / 2)}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {formatDuration(total)}
        </Typography>
      </Box>
    </Box>
  );
};

export default NetworkTimeline;
