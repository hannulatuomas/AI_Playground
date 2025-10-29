import { useParams, useNavigate } from 'react-router-dom';
import { LoadingSpinner } from '../common/LoadingSpinner';
import NotFound from '../common/NotFound';
import { AssetTypeForm } from '../assetTypes/AssetTypeForm';
import { useAssetType } from '../../hooks/useAssetType';
import { IAssetType } from '../../types/AssetType';

export const AssetTypeFormWrapper = () => {
  const { containerId, assetTypeId } = useParams<{ containerId: string; assetTypeId?: string }>();
  const navigate = useNavigate();
  const { assetType, isLoading, saveAssetType } = useAssetType(containerId!, assetTypeId);

  const handleSave = async (assetType: IAssetType) => {
    try {
      await saveAssetType(assetType);
      navigate(`/containers/${containerId}`);
    } catch (error) {
      // Error is already handled by the hook
    }
  };

  const handleCancel = () => {
    navigate(`/containers/${containerId}`);
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return containerId ? (
    <AssetTypeForm
      containerId={containerId}
      assetType={assetType}
      onSave={handleSave}
      onCancel={handleCancel}
    />
  ) : <NotFound />;
}; 