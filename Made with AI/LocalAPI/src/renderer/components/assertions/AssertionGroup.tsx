import React from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  PlayArrow as RunIcon,
  CheckCircle as PassIcon,
  Error as FailIcon,
} from '@mui/icons-material';
import AssertionBuilder from './AssertionBuilder';
import type { Assertion } from '../../../types/models';

interface AssertionGroupProps {
  name: string;
  assertions: Assertion[];
  onChange: (assertions: Assertion[]) => void;
  onDelete?: () => void;
  onRun?: () => void;
  expanded?: boolean;
  onExpandChange?: (expanded: boolean) => void;
}

const AssertionGroup: React.FC<AssertionGroupProps> = ({
  name,
  assertions,
  onChange,
  onDelete,
  onRun,
  expanded = true,
  onExpandChange,
}) => {
  const handleAddAssertion = () => {
    const newAssertion: Assertion = {
      id: `assertion-${Date.now()}`,
      type: 'status',
      enabled: true,
      operator: 'equals',
      expected: '200',
    };
    onChange([...assertions, newAssertion]);
  };

  const handleUpdateAssertion = (index: number, updated: Assertion) => {
    const newAssertions = [...assertions];
    newAssertions[index] = updated;
    onChange(newAssertions);
  };

  const handleDeleteAssertion = (index: number) => {
    onChange(assertions.filter((_, i) => i !== index));
  };

  const handleDuplicateAssertion = (index: number) => {
    const duplicate = {
      ...assertions[index],
      id: `assertion-${Date.now()}`,
    };
    onChange([...assertions, duplicate]);
  };

  const passedCount = assertions.filter((a) => a.result === true).length;
  const failedCount = assertions.filter((a) => a.result === false).length;
  const totalCount = assertions.length;
  const hasResults = assertions.some((a) => a.result !== undefined);

  return (
    <Accordion
      expanded={expanded}
      onChange={(_, isExpanded) => onExpandChange?.(isExpanded)}
      sx={{ mb: 2 }}
    >
      <AccordionSummary
        expandIcon={<ExpandMoreIcon />}
        sx={{
          bgcolor: 'background.paper',
          '&:hover': { bgcolor: 'action.hover' },
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1, mr: 2 }}>
          <Typography variant="subtitle1" fontWeight={600}>
            {name}
          </Typography>

          <Chip
            label={`${totalCount} assertion${totalCount !== 1 ? 's' : ''}`}
            size="small"
            variant="outlined"
          />

          {hasResults && (
            <>
              {passedCount > 0 && (
                <Chip
                  icon={<PassIcon />}
                  label={passedCount}
                  size="small"
                  color="success"
                  variant="outlined"
                />
              )}
              {failedCount > 0 && (
                <Chip
                  icon={<FailIcon />}
                  label={failedCount}
                  size="small"
                  color="error"
                  variant="outlined"
                />
              )}
            </>
          )}

          <Box sx={{ flex: 1 }} />

          {onRun && (
            <Tooltip title="Run Assertions">
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  onRun();
                }}
                color="primary"
              >
                <RunIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}

          {onDelete && (
            <Tooltip title="Delete Group">
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete();
                }}
                color="error"
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </AccordionSummary>

      <AccordionDetails>
        <Box>
          {assertions.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                No assertions defined
              </Typography>
              <Button
                startIcon={<AddIcon />}
                onClick={handleAddAssertion}
                size="small"
                sx={{ mt: 1 }}
              >
                Add First Assertion
              </Button>
            </Box>
          ) : (
            <>
              {assertions.map((assertion, index) => (
                <AssertionBuilder
                  key={assertion.id}
                  assertion={assertion}
                  onChange={(updated) => handleUpdateAssertion(index, updated)}
                  onDelete={() => handleDeleteAssertion(index)}
                  onDuplicate={() => handleDuplicateAssertion(index)}
                />
              ))}

              <Button
                startIcon={<AddIcon />}
                onClick={handleAddAssertion}
                variant="outlined"
                fullWidth
                sx={{ mt: 1 }}
              >
                Add Assertion
              </Button>
            </>
          )}
        </Box>
      </AccordionDetails>
    </Accordion>
  );
};

export default AssertionGroup;
