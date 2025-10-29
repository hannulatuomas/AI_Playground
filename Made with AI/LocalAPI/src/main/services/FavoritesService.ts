/**
 * FavoritesService - Bookmarks/Favorites Management
 * 
 * Manages user favorites for quick access to:
 * - Requests
 * - Collections
 * - Environments
 * - Variables
 * - Any other entity
 */

import * as fs from 'fs';
import * as path from 'path';
import { app } from 'electron';

export interface Favorite {
  id: string;
  type: 'request' | 'collection' | 'environment' | 'variable' | 'folder' | 'other';
  entityId: string; // ID of the favorited entity
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  tags: string[];
  folder?: string;
  order: number;
  createdAt: number;
  lastAccessedAt: number;
}

export interface FavoriteFolder {
  id: string;
  name: string;
  color?: string;
  order: number;
  collapsed?: boolean;
}

export class FavoritesService {
  private favorites: Map<string, Favorite>;
  private folders: Map<string, FavoriteFolder>;
  private favoritesPath: string;

  constructor(dataPath?: string) {
    const userDataPath = app?.getPath('userData') || process.cwd();
    this.favoritesPath = dataPath || path.join(userDataPath, 'favorites.json');
    this.favorites = new Map();
    this.folders = new Map();
    this.loadFavorites();
  }

  /**
   * Add to favorites
   */
  addFavorite(favorite: Omit<Favorite, 'id' | 'order' | 'createdAt' | 'lastAccessedAt'>): Favorite {
    const id = this.generateId();
    const newFavorite: Favorite = {
      ...favorite,
      id,
      order: this.favorites.size,
      createdAt: Date.now(),
      lastAccessedAt: Date.now(),
      tags: favorite.tags || [],
    };

    this.favorites.set(id, newFavorite);
    this.saveFavorites();
    return newFavorite;
  }

  /**
   * Remove from favorites
   */
  removeFavorite(id: string): boolean {
    const removed = this.favorites.delete(id);
    if (removed) {
      this.reorderFavorites();
      this.saveFavorites();
    }
    return removed;
  }

  /**
   * Get favorite by ID
   */
  getFavorite(id: string): Favorite | undefined {
    return this.favorites.get(id);
  }

  /**
   * Get all favorites
   */
  getAllFavorites(): Favorite[] {
    return Array.from(this.favorites.values()).sort((a, b) => a.order - b.order);
  }

  /**
   * Get favorites by type
   */
  getFavoritesByType(type: Favorite['type']): Favorite[] {
    return this.getAllFavorites().filter(fav => fav.type === type);
  }

  /**
   * Get favorites by folder
   */
  getFavoritesByFolder(folder: string): Favorite[] {
    return this.getAllFavorites().filter(fav => fav.folder === folder);
  }

  /**
   * Get favorites by tag
   */
  getFavoritesByTag(tag: string): Favorite[] {
    return this.getAllFavorites().filter(fav => fav.tags.includes(tag));
  }

  /**
   * Search favorites
   */
  searchFavorites(query: string): Favorite[] {
    if (!query.trim()) return this.getAllFavorites();

    const lowerQuery = query.toLowerCase();
    return this.getAllFavorites().filter(fav =>
      fav.name.toLowerCase().includes(lowerQuery) ||
      fav.description?.toLowerCase().includes(lowerQuery) ||
      fav.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
    );
  }

  /**
   * Check if entity is favorited
   */
  isFavorite(entityId: string): boolean {
    return Array.from(this.favorites.values()).some(fav => fav.entityId === entityId);
  }

  /**
   * Get favorite by entity ID
   */
  getFavoriteByEntityId(entityId: string): Favorite | undefined {
    return Array.from(this.favorites.values()).find(fav => fav.entityId === entityId);
  }

  /**
   * Toggle favorite
   */
  toggleFavorite(favorite: Omit<Favorite, 'id' | 'order' | 'createdAt' | 'lastAccessedAt'>): { added: boolean; favorite?: Favorite } {
    const existing = this.getFavoriteByEntityId(favorite.entityId);

    if (existing) {
      this.removeFavorite(existing.id);
      return { added: false };
    } else {
      const newFav = this.addFavorite(favorite);
      return { added: true, favorite: newFav };
    }
  }

  /**
   * Update favorite
   */
  updateFavorite(id: string, updates: Partial<Favorite>): boolean {
    const favorite = this.favorites.get(id);
    if (!favorite) return false;

    const updated = { ...favorite, ...updates };
    this.favorites.set(id, updated);
    this.saveFavorites();
    return true;
  }

  /**
   * Reorder favorite
   */
  reorderFavorite(id: string, newOrder: number): boolean {
    const favorite = this.favorites.get(id);
    if (!favorite) return false;

    const allFavorites = this.getAllFavorites();
    const currentIndex = allFavorites.findIndex(f => f.id === id);
    if (currentIndex === -1) return false;

    // Remove and reinsert
    allFavorites.splice(currentIndex, 1);
    allFavorites.splice(newOrder, 0, favorite);

    // Update orders
    allFavorites.forEach((fav, index) => {
      fav.order = index;
    });

    this.saveFavorites();
    return true;
  }

  /**
   * Create folder
   */
  createFolder(name: string, color?: string): FavoriteFolder {
    const id = this.generateId();
    const folder: FavoriteFolder = {
      id,
      name,
      color,
      order: this.folders.size,
      collapsed: false,
    };

    this.folders.set(id, folder);
    this.saveFavorites();
    return folder;
  }

  /**
   * Get folder by ID
   */
  getFolder(id: string): FavoriteFolder | undefined {
    return this.folders.get(id);
  }

  /**
   * Get all folders
   */
  getAllFolders(): FavoriteFolder[] {
    return Array.from(this.folders.values()).sort((a, b) => a.order - b.order);
  }

  /**
   * Update folder
   */
  updateFolder(id: string, updates: Partial<FavoriteFolder>): boolean {
    const folder = this.folders.get(id);
    if (!folder) return false;

    const updated = { ...folder, ...updates };
    this.folders.set(id, updated);
    this.saveFavorites();
    return true;
  }

  /**
   * Delete folder
   */
  deleteFolder(id: string): boolean {
    const folder = this.folders.get(id);
    if (!folder) return false;

    // Remove folder from all favorites
    for (const favorite of this.favorites.values()) {
      if (favorite.folder === id) {
        favorite.folder = undefined;
      }
    }

    this.folders.delete(id);
    this.saveFavorites();
    return true;
  }

  /**
   * Add favorite to folder
   */
  addToFolder(favoriteId: string, folderId: string): boolean {
    const favorite = this.favorites.get(favoriteId);
    const folder = this.folders.get(folderId);

    if (!favorite || !folder) return false;

    favorite.folder = folderId;
    this.saveFavorites();
    return true;
  }

  /**
   * Remove favorite from folder
   */
  removeFromFolder(favoriteId: string): boolean {
    const favorite = this.favorites.get(favoriteId);
    if (!favorite) return false;

    favorite.folder = undefined;
    this.saveFavorites();
    return true;
  }

  /**
   * Get recently accessed favorites
   */
  getRecentFavorites(limit: number = 10): Favorite[] {
    return this.getAllFavorites()
      .sort((a, b) => b.lastAccessedAt - a.lastAccessedAt)
      .slice(0, limit);
  }

  /**
   * Access favorite (update last accessed time)
   */
  accessFavorite(id: string): boolean {
    const favorite = this.favorites.get(id);
    if (!favorite) return false;

    favorite.lastAccessedAt = Date.now();
    this.saveFavorites();
    return true;
  }

  /**
   * Get all tags
   */
  getAllTags(): string[] {
    const tags = new Set<string>();
    for (const favorite of this.favorites.values()) {
      favorite.tags.forEach(tag => tags.add(tag));
    }
    return Array.from(tags).sort();
  }

  /**
   * Export favorites
   */
  exportFavorites(filePath: string): void {
    const data = {
      favorites: this.getAllFavorites(),
      folders: this.getAllFolders(),
    };

    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
  }

  /**
   * Import favorites
   */
  importFavorites(filePath: string): void {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

    if (data.folders) {
      for (const folder of data.folders) {
        this.folders.set(folder.id, folder);
      }
    }

    if (data.favorites) {
      for (const favorite of data.favorites) {
        this.favorites.set(favorite.id, favorite);
      }
    }

    this.saveFavorites();
  }

  /**
   * Clear all favorites
   */
  clearAll(): void {
    this.favorites.clear();
    this.folders.clear();
    this.saveFavorites();
  }

  /**
   * Get favorites count
   */
  getCount(): number {
    return this.favorites.size;
  }

  /**
   * Save favorites to file
   */
  private saveFavorites(): void {
    try {
      const dir = path.dirname(this.favoritesPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }

      const data = {
        favorites: this.getAllFavorites(),
        folders: this.getAllFolders(),
      };

      fs.writeFileSync(this.favoritesPath, JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('Error saving favorites:', error);
    }
  }

  /**
   * Load favorites from file
   */
  private loadFavorites(): void {
    try {
      if (fs.existsSync(this.favoritesPath)) {
        const data = JSON.parse(fs.readFileSync(this.favoritesPath, 'utf-8'));

        if (data.folders) {
          for (const folder of data.folders) {
            this.folders.set(folder.id, folder);
          }
        }

        if (data.favorites) {
          for (const favorite of data.favorites) {
            this.favorites.set(favorite.id, favorite);
          }
        }
      }
    } catch (error) {
      console.error('Error loading favorites:', error);
    }
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `fav-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Reorder all favorites
   */
  private reorderFavorites(): void {
    const allFavorites = this.getAllFavorites();
    allFavorites.forEach((fav, index) => {
      fav.order = index;
    });
  }
}
