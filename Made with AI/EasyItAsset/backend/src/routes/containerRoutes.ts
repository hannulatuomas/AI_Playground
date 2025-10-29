import { Router } from 'express';
import { ContainerController } from '../controllers/ContainerController';
import { ContainerService } from '../services/ContainerService';

export const createContainerRoutes = (containerService: ContainerService) => {
  const router = Router();
  const controller = new ContainerController(containerService);

  // Bind controller methods to the router
  router.post('/', (req, res) => controller.createContainer(req, res));
  router.get('/', (req, res) => controller.getContainers(req, res));
  router.get('/:containerId', (req, res) => controller.getContainer(req, res));
  router.put('/:containerId', (req, res) => controller.updateContainer(req, res));
  router.delete('/:containerId', (req, res) => controller.deleteContainer(req, res));

  return router;
}; 