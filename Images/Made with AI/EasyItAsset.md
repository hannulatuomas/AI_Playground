# Asset Management System

A full-stack application for managing assets, containers, and their types with a modern React frontend and Node.js backend.

## Application Flow

### 1. Container Creation
- User starts at the `CreateContainer` component
- A new `Container` object is created with:
  - Unique ID (generated using `IdUtils.generateContainerId()`)
  - Name and description
  - Empty asset types array
- The container is stored in local state but not yet saved to backend

### 2. Asset Type Creation
- User clicks "Add Asset Type" in the container
- A new `AssetType` object is created with:
  - Unique ID (using `IdUtils.generateAssetTypeId(containerId)`)
  - Reference to parent container ID
  - Name and label
  - Empty fields and subtypes arrays
- The asset type is added to the container's `assetTypes` array

### 3. Field Management
- User adds fields to the asset type in the `AssetTypeForm`
- Each new `FieldConfig` object includes:
  - Unique ID (using `IdUtils.generateFieldId(assetTypeId)`)
  - Reference to parent asset type ID
  - Field properties:
    - Name and label
    - Type (Text, Number, Date, Select, MultiSelect)
    - Required flag
    - Validation options (based on field type)
    - Default value
- Fields are added to the asset type's `fields` array

### 4. Subtype Management
- User adds subtypes to the asset type
- Each new `AssetSubType` object includes:
  - Unique ID (using `IdUtils.generateSubtypeId(assetTypeId)`)
  - Reference to parent asset type ID
  - Name and label
  - Empty fields array
- Subtypes are added to the asset type's `subtypes` array

### 5. Subtype Field Management
- User adds fields to subtypes
- Fields for subtypes follow the same structure as asset type fields
- Each field includes:
  - Unique ID (using `IdUtils.generateFieldId(subtypeId)`)
  - Reference to parent subtype ID
  - All standard field properties and validations

### 6. Edit and Delete Operations
- Users can:
  - Edit any object (container, asset type, field, subtype)
  - Delete objects (with cascading deletion of child objects)
  - Cancel creation of new objects
- All changes are tracked in local state until final save

### 7. Asset Type Save
- When an asset type is saved:
  - All changes are updated in the container's state
  - The asset type becomes visible in the UI
  - Users can:
    - View the asset type
    - Edit it again
    - Delete it
  - No backend communication occurs yet

### 8. Container Save
- When the container is finally saved:
  - The complete container object is sent to the backend
  - The object includes:
    - Container details
    - All asset types
    - All fields
    - All subtypes
    - All subtype fields
- Backend processing:
  - Container data → `containers.csv`
  - Asset types → `asset_types.csv`
  - Fields → `fields.csv`
  - Subtypes → `subtypes.csv`
  - All relationships maintained through IDs

## Data Structure

### Container
```typescript
interface IContainer {
  id: string;
  name: string;
  description: string;
  assetTypes: IAssetTypeConfig[];
  createdAt: string;
  updatedAt: string;
}
```

### Asset Type
```typescript
interface IAssetTypeConfig {
  id: string;
  name: string;
  label: string;
  containerId: string;
  fields: IFieldConfig[];
  subtypes: IAssetSubType[];
  createdAt: string;
  updatedAt: string;
}
```

### Field
```typescript
interface IFieldConfig {
  id: string;
  name: string;
  type: FieldType;
  label?: string;
  parentTypeId: string;
  required?: boolean;
  defaultValue?: string;
  length?: number;
  description?: string;
  // Text field validation
  pattern?: string;
  // Number field validation
  min?: number;
  max?: number;
  step?: number;
  // Date field validation
  minDate?: string;
  maxDate?: string;
  // Select/MultiSelect options
  options?: string[];
  createdAt: string;
  updatedAt: string;
}
```

### Subtype
```typescript
interface IAssetSubType {
  id: string;
  name: string;
  label: string;
  parentTypeId: string;
  fields: IFieldConfig[];
  createdAt: string;
  updatedAt: string;
}
```

## Key Features

- **Hierarchical Data Structure**: Containers → Asset Types → Fields/Subtypes → Fields
- **Type-Specific Validation**: Different validation options based on field type
- **Real-time Preview**: All changes visible in UI before backend save
- **Cascading Operations**: Delete operations properly handle child objects
- **ID Management**: Unique IDs generated and maintained for all objects
- **Relationship Tracking**: All parent-child relationships maintained through IDs

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── containers/
│   │   │   ├── ContainerList.tsx
│   │   │   ├── ContainerView.tsx
│   │   │   └── CreateContainer.tsx
│   │   ├── assetTypes/
│   │   │   ├── AssetTypeForm.tsx
│   │   │   ├── AssetTypeList.tsx
│   │   │   └── AssetTypeView.tsx
│   │   ├── assetSubTypes/
│   │   │   ├── AssetSubTypeForm.tsx
│   │   │   ├── AssetSubTypeList.tsx
│   │   │   └── AssetSubTypeView.tsx
│   │   └── common/
│   │       ├── DynamicForm.tsx
│   │       ├── FieldRenderer.tsx
│   │       ├── LoadingSpinner.tsx
│   │       ├── Modal.tsx
│   │       ├── Tooltip.tsx
│   │       └── Toast.tsx
│   ├── services/
│   │   ├── ContainerService.ts
│   │   ├── AssetTypeService.ts
│   │   ├── AssetSubTypeService.ts
│   │   ├── UserService.ts
│   │   └── BaseService.ts
│   ├── types/
│   │   ├── Container.ts
│   │   ├── AssetType.ts
│   │   ├── AssetSubType.ts
│   │   ├── FieldConfig.ts
│   │   └── User.ts
│   ├── utils/
│   │   ├── IdUtils.ts
│   │   ├── ValidationUtils.ts
│   │   └── DateUtils.ts
│   ├── context/
│   │   └── UserContext.tsx
│   ├── hooks/
│   │   ├── useUser.ts
│   │   └── useToast.ts
│   └── App.tsx
│
backend/
├── src/
│   ├── controllers/
│   │   ├── ContainerController.ts
│   │   ├── AssetTypeController.ts
│   │   ├── AssetSubTypeController.ts
│   │   └── UserController.ts
│   ├── services/
│   │   ├── ContainerService.ts
│   │   ├── AssetTypeService.ts
│   │   ├── AssetSubTypeService.ts
│   │   └── UserService.ts
│   ├── models/
│   │   ├── Container.ts
│   │   ├── AssetType.ts
│   │   ├── AssetSubType.ts
│   │   └── User.ts
│   ├── utils/
│   │   ├── IdUtils.ts
│   │   ├── ValidationUtils.ts
│   │   └── FileUtils.ts
│   └── app.ts
└── data/
    ├── containers.csv
    ├── asset_types.csv
    ├── fields.csv
    ├── subtypes.csv
    └── users.csv
```

### Frontend Structure

#### Components
- **Containers**: Components for managing containers
  - `ContainerList`: Displays list of containers
  - `ContainerView`: Shows container details
  - `CreateContainer`: Form for creating/editing containers

- **Asset Types**: Components for managing asset types
  - `AssetTypeForm`: Form for creating/editing asset types
  - `AssetTypeList`: Displays list of asset types
  - `AssetTypeView`: Shows asset type details

- **Asset Subtypes**: Components for managing subtypes
  - `AssetSubTypeForm`: Form for creating/editing subtypes
  - `AssetSubTypeList`: Displays list of subtypes
  - `AssetSubTypeView`: Shows subtype details

- **Common**: Reusable components
  - `DynamicForm`: Generates forms based on field configurations
  - `FieldRenderer`: Renders appropriate input controls
  - `LoadingSpinner`: Loading indicator
  - `Modal`: Reusable modal component
  - `Tooltip`: Tooltip component
  - `Toast`: Notification component

#### Services
- `ContainerService`: Handles container-related API calls
- `AssetTypeService`: Handles asset type-related API calls
- `AssetSubTypeService`: Handles subtype-related API calls
- `UserService`: Handles user authentication and management
- `BaseService`: Provides common functionality for API calls

#### Types
- `Container.ts`: Container interface and types
- `AssetType.ts`: Asset type interface and types
- `AssetSubType.ts`: Subtype interface and types
- `FieldConfig.ts`: Field configuration interface and types
- `User.ts`: User interface and types

#### Utils
- `IdUtils.ts`: ID generation and validation
- `ValidationUtils.ts`: Validation helper functions
- `DateUtils.ts`: Date formatting and manipulation

#### Context
- `UserContext.tsx`: Manages user authentication state

#### Hooks
- `useUser.ts`: Custom hook for user context
- `useToast.ts`: Custom hook for toast notifications

### Backend Structure

#### Controllers
- `ContainerController`: Handles container-related routes
- `AssetTypeController`: Handles asset type-related routes
- `AssetSubTypeController`: Handles subtype-related routes
- `UserController`: Handles user-related routes

#### Services
- `ContainerService`: Business logic for containers
- `AssetTypeService`: Business logic for asset types
- `AssetSubTypeService`: Business logic for subtypes
- `UserService`: Business logic for users

#### Models
- `Container.ts`: Container data model
- `AssetType.ts`: Asset type data model
- `AssetSubType.ts`: Subtype data model
- `User.ts`: User data model

#### Utils
- `IdUtils.ts`: ID generation and validation
- `ValidationUtils.ts`: Data validation
- `FileUtils.ts`: CSV file operations

#### Data
- `containers.csv`: Container data storage
- `asset_types.csv`: Asset type data storage
- `fields.csv`: Field configuration storage
- `subtypes.csv`: Subtype data storage
- `users.csv`: User data storage

## Features

- **User Management**
  - User authentication and authorization
  - Role-based access control
  - User context management
  - Secure token handling

- **Asset Type Management**
  - Create and manage different asset types
  - Customize fields with various types (Text, Number, Date, Boolean, Select, MultiSelect)
  - Define validation rules for each field
  - Support for required fields and default values

- **Asset Subtype Management**
  - Create subtypes that inherit from parent asset types
  - Override field configurations
  - Hide inherited fields
  - Add new subtype-specific fields

- **Field Validation**
  - Comprehensive validation system
  - Support for various validation rules:
    - Required fields
    - Pattern matching
    - Min/max values
    - Min/max length
    - Date ranges
    - Custom validation messages

- **User Interface**
  - Modern, responsive design
  - Form validation with real-time feedback
  - Dynamic form generation based on asset type configuration
  - Support for various field types with appropriate input controls

## Key Components

### Services
- `AssetTypeService`: Handles CRUD operations for asset types
- `AssetSubTypeService`: Handles CRUD operations for asset subtypes
- `BaseService`: Provides common functionality for API calls

### Validation
- `AssetTypeValidator`: Validates asset type configurations
- `AssetSubTypeValidator`: Validates asset subtype configurations
- `FieldValidator`: Validates individual field configurations

### Utilities
- `AssetTypeUtils`: Handles conversion between frontend and backend formats for asset types
- `FieldUtils`: Handles conversion between frontend and backend formats for fields

### Components
- `AssetTypeForm`: Form for creating and editing asset types
- `AssetSubTypeForm`: Form for creating and editing asset subtypes
- `DynamicForm`: Generates forms based on field configurations
- `FieldRenderer`: Renders appropriate input controls based on field type

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```

### Debug User
For development and testing purposes, the application automatically logs in with a debug user. This user has the following credentials:

```typescript
{
  id: 'u-{unique_id}', // Generated using IdUtils.generateUserId()
  username: 'debug-user',
  email: 'debug@example.com',
  role: 'admin',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString()
}
```

The debug user is automatically logged in when:
- No user is currently logged in
- The application starts
- After a manual logout

This feature is implemented in `UserContext.tsx` and uses `UserService` for authentication. The debug user has admin privileges, allowing full access to all features during development.

Note: This is for development purposes only. In production, proper authentication should be implemented.

## Development

### Adding New Field Types
1. Update `FieldType` enum in `FieldConfig.ts`
2. Add validation rules in `FieldValidator.ts`
3. Add conversion logic in `FieldUtils.ts`
4. Update `FieldRenderer.tsx` to handle the new field type

### Adding New Validation Rules
1. Update `ValidationRule` interface in `FieldConfig.ts`
2. Add validation logic in `FieldValidator.ts`
3. Update form components to handle the new validation rules

## Best Practices

- Always validate data before sending to the backend
- Use appropriate field types for different data
- Provide clear validation messages
- Keep field names unique within an asset type
- Use meaningful labels for fields
- Consider performance when adding many fields

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## To Do

### Authentication & Security
- [ ] Update the login method in UserService to make actual API calls
- [ ] Add proper error handling and validation for authentication
- [ ] Implement token management and refresh mechanism
- [ ] Add protected routes with role-based access
- [ ] Update the UI to show login/logout buttons
- [ ] Implement JWT token refresh mechanism
- [ ] Add audit logging for sensitive operations
- [ ] Implement IP whitelisting
- [ ] Add request signing for critical operations

### Core Features
- [ ] Add support for nested asset types (assets within assets)
- [ ] Implement asset relationships and references
- [ ] Add bulk operations for assets (import/export)
- [ ] Add search functionality with advanced filters
- [ ] Implement asset versioning and history tracking

### User Experience
- [ ] Add drag-and-drop field reordering in forms
- [ ] Implement field templates for quick field creation
- [ ] Add field grouping and sections in forms
- [ ] Create a field preview mode
- [ ] Add keyboard shortcuts for common actions

### Validation & Data Integrity
- [ ] Add cross-field validation rules
- [ ] Implement validation rule templates
- [ ] Add validation rule testing interface
- [ ] Support for custom validation functions
- [ ] Add validation rule dependencies

### Performance
- [ ] Implement lazy loading for large forms
- [ ] Add caching for frequently accessed asset types
- [ ] Optimize form rendering for large numbers of fields
- [ ] Add pagination for asset lists
- [ ] Implement virtual scrolling for long lists

### Security
- [ ] Add role-based access control
- [ ] Implement field-level permissions
- [ ] Add audit logging for changes
- [ ] Implement data encryption for sensitive fields
- [ ] Add two-factor authentication

### Testing & Quality
- [ ] Add unit tests for validators
- [ ] Implement integration tests for services
- [ ] Add end-to-end tests for forms
- [ ] Set up continuous integration
- [ ] Add code coverage reporting

### Documentation
- [ ] Add API documentation
- [ ] Create user guides
- [ ] Add developer documentation
- [ ] Create example configurations
- [ ] Add troubleshooting guide

### Integration
- [ ] Add support for external data sources
- [ ] Implement webhook system for events
- [ ] Add API for third-party integrations
- [ ] Support for custom field renderers
- [ ] Add plugin system for extensions

### Performance Improvements
- [ ] Implement caching for frequently accessed data
- [ ] Add batch operations for bulk updates
- [ ] Optimize file system operations
- [ ] Add database support for better performance
- [ ] Implement data compression for large files

### Security Enhancements
- [ ] Add JWT token refresh mechanism
- [ ] Implement role-based access control (RBAC)
- [ ] Add audit logging for sensitive operations
- [ ] Implement IP whitelisting
- [ ] Add request signing for critical operations

### Testing
- [ ] Add comprehensive unit tests
- [ ] Implement integration tests
- [ ] Add end-to-end tests
- [ ] Set up CI/CD pipeline
- [ ] Add performance testing

### Documentation
- [ ] Add API documentation
- [ ] Create user guides
- [ ] Add architecture diagrams
- [ ] Document deployment procedures
- [ ] Add troubleshooting guide

### Features
- [ ] Add asset versioning
- [ ] Implement asset relationships
- [ ] Add bulk import/export functionality
- [ ] Add custom field types
- [ ] Implement asset templates

### Monitoring
- [ ] Add application metrics
- [ ] Implement error tracking
- [ ] Add performance monitoring
- [ ] Set up alerting system
- [ ] Add usage analytics

### User Experience
- [ ] Add keyboard shortcuts
- [ ] Implement drag-and-drop functionality
- [ ] Add bulk actions
- [ ] Improve form validation feedback
- [ ] Add search filters

### Infrastructure
- [ ] Containerize the application
- [ ] Add Kubernetes support
- [ ] Implement auto-scaling
- [ ] Add backup and restore functionality
- [ ] Set up monitoring infrastructure

## ID System Implementation
- [x] Implement hierarchical ID system with the following structure:
  - User ID: `u-{unique_id}`
  - Container ID: `u-{user_id}-c-{container_id}`
  - Asset Type ID: `u-{user_id}-c-{container_id}-at-{asset_type_id}`
  - Asset ID: `u-{user_id}-c-{container_id}-at-{asset_type_id}-a-{asset_id}`
  - Subtype ID: `u-{user_id}-c-{container_id}-at-{asset_type_id}-st-{subtype_id}-a-{asset_id}`
  - Field ID: `{parent_id}-f-{field_id}`
- [x] Add ID validation patterns for each type
- [x] Implement methods to extract specific parts of IDs
- [x] Add methods to check if an ID belongs to a specific user/container/etc.
- [x] Add methods to generate IDs in bulk
- [x] Add error handling for invalid ID formats
- [x] Update all services to use the new ID system
- [x] Add tests for ID generation and validation
- [x] Document ID system usage in code comments

## License

This project is licensed under the MIT License - see the LICENSE file for details.


