import { useParams, useNavigate } from 'react-router-dom';
import { IAsset } from '../../types/Asset';
import NotFound from '../common/NotFound';
import AssetForm from '../assets/AssetForm';
import { useAsset } from '../../hooks/useAsset';
import { LoadingSpinner } from '../common/LoadingSpinner';

export const AssetFormWrapper = () => {
  const { containerId, assetId } = useParams<{ containerId: string; assetId?: string }>();
  const navigate = useNavigate();
  const { asset, isLoading, saveAsset } = useAsset(containerId!, assetId);

  const handleSave = async (assetData: IAsset) => {
    try {
      await saveAsset(assetData);
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
    <AssetForm
      containerId={containerId}
      asset={asset}
      onSave={handleSave}
      onCancel={handleCancel}
    />
  ) : <NotFound />;
}; 