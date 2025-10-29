import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { IContainer } from '../types/Container';
import { ContainerService } from '../services/ContainerService';

interface UseContainerResult {
  container: IContainer | undefined;
  isLoading: boolean;
  error: Error | null;
  saveContainer: (container: Partial<IContainer>) => Promise<void>;
  deleteContainer: () => Promise<void>;
}

export const useContainer = (containerId: string): UseContainerResult => {
  const [container, setContainer] = useState<IContainer | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const loadContainer = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const containerService = ContainerService.getInstance();
        const data = await containerService.getContainer(containerId);
        setContainer(data);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to load container');
        setError(error);
        toast.error('Failed to load container');
      } finally {
        setIsLoading(false);
      }
    };

    loadContainer();
  }, [containerId]);

  const saveContainer = async (containerData: Partial<IContainer>) => {
    try {
      setIsLoading(true);
      setError(null);
      const containerService = ContainerService.getInstance();
      const updatedContainer = await containerService.updateContainer(containerId, containerData);
      setContainer(updatedContainer);
      toast.success('Container saved successfully');
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to save container');
      setError(error);
      toast.error('Failed to save container');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const deleteContainer = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const containerService = ContainerService.getInstance();
      await containerService.deleteContainer(containerId);
      toast.success('Container deleted successfully');
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to delete container');
      setError(error);
      toast.error('Failed to delete container');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return { container, isLoading, error, saveContainer, deleteContainer };
}; 