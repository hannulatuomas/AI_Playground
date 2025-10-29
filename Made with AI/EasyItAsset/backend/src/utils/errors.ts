export enum ErrorCode {
  // General errors (1000-1999)
  UNKNOWN_ERROR = 1000,
  INVALID_INPUT = 1001,
  RESOURCE_NOT_FOUND = 1002,
  UNAUTHORIZED = 1003,
  FORBIDDEN = 1004,
  RATE_LIMIT_EXCEEDED = 1005,

  // File system errors (2000-2999)
  FILE_NOT_FOUND = 2000,
  FILE_READ_ERROR = 2001,
  FILE_WRITE_ERROR = 2002,
  FILE_DELETE_ERROR = 2003,
  INVALID_FILE_FORMAT = 2004,
  FILE_ACCESS_DENIED = 2005,

  // Validation errors (3000-3999)
  VALIDATION_ERROR = 3000,
  REQUIRED_FIELD_MISSING = 3001,
  INVALID_FIELD_TYPE = 3002,
  INVALID_FIELD_VALUE = 3003,
  DUPLICATE_ENTRY = 3004,
  INVALID_DATE_FORMAT = 3005,
  INVALID_REGEX_PATTERN = 3006,

  // Transaction errors (4000-4999)
  TRANSACTION_FAILED = 4000,
  ROLLBACK_FAILED = 4001,
  COMMIT_FAILED = 4002,

  // Asset errors (5000-5999)
  ASSET_NOT_FOUND = 5000,
  ASSET_CREATION_FAILED = 5001,
  ASSET_UPDATE_FAILED = 5002,
  ASSET_DELETE_FAILED = 5003,
  INVALID_ASSET_TYPE = 5004,
  INVALID_ASSET_SUBTYPE = 5005,

  // Container errors (6000-6999)
  CONTAINER_NOT_FOUND = 6000,
  CONTAINER_CREATION_FAILED = 6001,
  CONTAINER_UPDATE_FAILED = 6002,
  CONTAINER_DELETE_FAILED = 6003,
  INVALID_CONTAINER_NAME = 6004
}

export class AppError extends Error {
  constructor(
    public code: ErrorCode,
    public message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export const getErrorMessage = (code: ErrorCode, details?: any): string => {
  switch (code) {
    case ErrorCode.UNKNOWN_ERROR:
      return 'An unknown error occurred';
    case ErrorCode.INVALID_INPUT:
      return 'Invalid input provided';
    case ErrorCode.RESOURCE_NOT_FOUND:
      return `Resource not found: ${details?.resource || 'unknown'}`;
    case ErrorCode.UNAUTHORIZED:
      return 'Unauthorized access';
    case ErrorCode.FORBIDDEN:
      return 'Access forbidden';
    case ErrorCode.RATE_LIMIT_EXCEEDED:
      return 'Rate limit exceeded. Please try again later';
    case ErrorCode.FILE_NOT_FOUND:
      return `File not found: ${details?.filePath || 'unknown'}`;
    case ErrorCode.FILE_READ_ERROR:
      return `Error reading file: ${details?.filePath || 'unknown'}`;
    case ErrorCode.FILE_WRITE_ERROR:
      return `Error writing to file: ${details?.filePath || 'unknown'}`;
    case ErrorCode.FILE_DELETE_ERROR:
      return `Error deleting file: ${details?.filePath || 'unknown'}`;
    case ErrorCode.INVALID_FILE_FORMAT:
      return `Invalid file format: ${details?.filePath || 'unknown'}`;
    case ErrorCode.FILE_ACCESS_DENIED:
      return `Access denied to file: ${details?.filePath || 'unknown'}`;
    case ErrorCode.VALIDATION_ERROR:
      return `Validation error: ${details?.field || 'unknown field'}`;
    case ErrorCode.REQUIRED_FIELD_MISSING:
      return `Required field missing: ${details?.field || 'unknown field'}`;
    case ErrorCode.INVALID_FIELD_TYPE:
      return `Invalid field type: ${details?.field || 'unknown field'}`;
    case ErrorCode.INVALID_FIELD_VALUE:
      return `Invalid field value: ${details?.field || 'unknown field'}`;
    case ErrorCode.DUPLICATE_ENTRY:
      return `Duplicate entry: ${details?.field || 'unknown field'}`;
    case ErrorCode.INVALID_DATE_FORMAT:
      return `Invalid date format: ${details?.field || 'unknown field'}`;
    case ErrorCode.INVALID_REGEX_PATTERN:
      return `Invalid regex pattern: ${details?.pattern || 'unknown pattern'}`;
    case ErrorCode.TRANSACTION_FAILED:
      return 'Transaction failed';
    case ErrorCode.ROLLBACK_FAILED:
      return 'Failed to rollback transaction';
    case ErrorCode.COMMIT_FAILED:
      return 'Failed to commit transaction';
    case ErrorCode.ASSET_NOT_FOUND:
      return `Asset not found: ${details?.assetId || 'unknown'}`;
    case ErrorCode.ASSET_CREATION_FAILED:
      return 'Failed to create asset';
    case ErrorCode.ASSET_UPDATE_FAILED:
      return 'Failed to update asset';
    case ErrorCode.ASSET_DELETE_FAILED:
      return 'Failed to delete asset';
    case ErrorCode.INVALID_ASSET_TYPE:
      return `Invalid asset type: ${details?.typeId || 'unknown'}`;
    case ErrorCode.INVALID_ASSET_SUBTYPE:
      return `Invalid asset subtype: ${details?.subtypeId || 'unknown'}`;
    case ErrorCode.CONTAINER_NOT_FOUND:
      return `Container not found: ${details?.containerId || 'unknown'}`;
    case ErrorCode.CONTAINER_CREATION_FAILED:
      return 'Failed to create container';
    case ErrorCode.CONTAINER_UPDATE_FAILED:
      return 'Failed to update container';
    case ErrorCode.CONTAINER_DELETE_FAILED:
      return 'Failed to delete container';
    case ErrorCode.INVALID_CONTAINER_NAME:
      return `Invalid container name: ${details?.name || 'unknown'}`;
    default:
      return 'An unknown error occurred';
  }
}; 