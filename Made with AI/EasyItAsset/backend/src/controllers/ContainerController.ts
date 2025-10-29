import { Request, Response } from 'express';
import { ContainerService } from '../services/ContainerService';
import { logger } from '../services/logger';

export class ContainerController {
  constructor(private containerService: ContainerService) {}

  public getContainers = async (req: Request, res: Response): Promise<void> => {
    try {
      const containers = await this.containerService.getContainers();
      res.status(200).json(containers);
    } catch (error) {
      logger.error('Error getting containers:', error);
      res.status(500).json({ error: 'Failed to get containers' });
    }
  };

  public getContainer = async (req: Request, res: Response): Promise<void> => {
    try {
      const { containerId } = req.params;
      const container = await this.containerService.getContainer(containerId);
      if (!container) {
        res.status(404).json({ error: 'Container not found' });
        return;
      }
      res.status(200).json(container);
    } catch (error) {
      logger.error('Error getting container:', error);
      res.status(500).json({ error: 'Failed to get container' });
    }
  };

  public createContainer = async (req: Request, res: Response): Promise<void> => {
    try {
      const container = await this.containerService.saveContainer(req.body);
      res.status(201).json(container);
    } catch (error) {
      logger.error('Error creating container:', error);
      res.status(500).json({ error: 'Failed to create container' });
    }
  };

  public updateContainer = async (req: Request, res: Response): Promise<void> => {
    try {
      const { containerId } = req.params;
      const container = await this.containerService.saveContainer({
        ...req.body,
        id: containerId
      });
      res.status(200).json(container);
    } catch (error) {
      logger.error('Error updating container:', error);
      res.status(500).json({ error: 'Failed to update container' });
    }
  };

  public deleteContainer = async (req: Request, res: Response): Promise<void> => {
    try {
      const { containerId } = req.params;
      await this.containerService.deleteContainer(containerId);
      res.status(204).send();
    } catch (error) {
      logger.error('Error deleting container:', error);
      res.status(500).json({ error: 'Failed to delete container' });
    }
  };
} 