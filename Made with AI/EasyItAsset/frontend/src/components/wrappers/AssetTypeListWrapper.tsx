import { useParams } from 'react-router-dom';
import { IAssetTypeConfig } from '../../types/FieldConfig';
import NotFound from '../common/NotFound';
import AssetTypeList from '../assetTypes/AssetTypeList';

export const AssetTypeListWrapper = () => {
  const { containerId } = useParams<{ containerId: string }>();
  
  const handleEdit = (assetType: IAssetTypeConfig) => {
    console.log('Edit asset type:', assetType);
  };
  
  const handleDelete = (assetTypeId: string) => {
    console.log('Delete asset type:', assetTypeId);
  };
  
  return containerId ? (
    <AssetTypeList
      assetTypes={[]} // TODO: Fetch asset types for this container
      onEdit={handleEdit}
      onDelete={handleDelete}
    />
  ) : <NotFound />;
}; 