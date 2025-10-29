import React from 'react';
import { IAssetTypeConfig } from '../../types/FieldConfig';

interface AssetTypeListProps {
  assetTypes: IAssetTypeConfig[];
  onEdit: (type: IAssetTypeConfig) => void;
  onDelete: (typeId: string) => void;
  isLoading?: boolean;
}

const AssetTypeList: React.FC<AssetTypeListProps> = ({
  assetTypes,
  onEdit,
  onDelete,
  isLoading = false
}) => {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (assetTypes.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No asset types</h3>
        <p className="mt-1 text-sm text-gray-500">Get started by creating a new asset type.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <ul className="divide-y divide-gray-200">
        {assetTypes.map(type => (
          <li key={type.id} className="hover:bg-gray-50 transition-colors duration-150">
            <div className="px-4 py-4 sm:px-6">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-indigo-600 truncate">
                    {type.label}
                  </p>
                  <p className="mt-1 text-sm text-gray-500">
                    {type.name}
                  </p>
                </div>
                <div className="ml-4 flex-shrink-0 flex space-x-3">
                  <button
                    onClick={() => onEdit(type)}
                    className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onDelete(type.id)}
                    className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    Delete
                  </button>
                </div>
              </div>
              {type.subtypes && type.subtypes.length > 0 && (
                <div className="mt-3">
                  <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Subtypes
                  </h4>
                  <ul className="mt-2 space-y-1">
                    {type.subtypes.map(subtype => (
                      <li key={subtype.id} className="text-sm text-gray-600 flex items-center">
                        <svg
                          className="h-4 w-4 text-gray-400 mr-2"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 5l7 7-7 7"
                          />
                        </svg>
                        {subtype.label}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AssetTypeList; 