/**
 * Entity Context Hook
 *
 * Manages the current entity context for multi-tenant support.
 * Provides functions to switch between entities.
 */

import { useState, useEffect, useCallback, createContext, useContext, ReactNode } from 'react';
import { entities as entitiesApi } from '../services/api';
import type { EntityBrief } from '../types';

// ========================
// Context
// ========================

interface EntityContextType {
  currentEntity: EntityBrief | null;
  entities: EntityBrief[];
  isLoading: boolean;
  error: string | null;
  switchEntity: (entityId: number) => Promise<void>;
  refreshEntities: () => Promise<void>;
}

const EntityContext = createContext<EntityContextType | null>(null);

const ENTITY_STORAGE_KEY = 'pharmalert-entity-id';

// ========================
// Provider
// ========================

export function EntityProvider({ children }: { children: ReactNode }) {
  const [currentEntity, setCurrentEntity] = useState<EntityBrief | null>(null);
  const [entities, setEntities] = useState<EntityBrief[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshEntities = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await entitiesApi.brief();
      setEntities(data);

      // Restore saved entity from localStorage
      const savedEntityId = localStorage.getItem(ENTITY_STORAGE_KEY);
      if (savedEntityId) {
        const savedEntity = data.find(e => e.id === parseInt(savedEntityId, 10));
        if (savedEntity) {
          setCurrentEntity(savedEntity);
          return;
        }
      }

      // Get default entity from backend
      const defaultEntity = await entitiesApi.getMyDefaultEntity();
      if (defaultEntity) {
        setCurrentEntity(defaultEntity);
        localStorage.setItem(ENTITY_STORAGE_KEY, String(defaultEntity.id));
      } else if (data.length > 0) {
        setCurrentEntity(data[0]);
        localStorage.setItem(ENTITY_STORAGE_KEY, String(data[0].id));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement des établissements');
      console.error('Failed to load entities:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshEntities();
  }, [refreshEntities]);

  const switchEntity = useCallback(async (entityId: number) => {
    const entity = entities.find(e => e.id === entityId);
    if (entity) {
      setCurrentEntity(entity);
      localStorage.setItem(ENTITY_STORAGE_KEY, String(entityId));
    }
  }, [entities]);

  return (
    <EntityContext.Provider value={{
      currentEntity,
      entities,
      isLoading,
      error,
      switchEntity,
      refreshEntities,
    }}>
      {children}
    </EntityContext.Provider>
  );
}

// ========================
// Hook
// ========================

export function useEntity() {
  const context = useContext(EntityContext);
  if (!context) {
    throw new Error('useEntity must be used within an EntityProvider');
  }
  return context;
}

// ========================
// Helper: Get entity ID for API calls
// ========================

export function getCurrentEntityId(): number | null {
  const stored = localStorage.getItem(ENTITY_STORAGE_KEY);
  return stored ? parseInt(stored, 10) : null;
}

// ========================
// Helper: Axios/fetch interceptor helper
// ========================

export function getEntityHeaders(): Record<string, string> {
  const entityId = getCurrentEntityId();
  if (entityId) {
    return { 'X-Entity-ID': String(entityId) };
  }
  return {};
}