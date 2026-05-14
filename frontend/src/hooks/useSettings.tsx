/**
 * Settings Hook
 *
 * Manages system configuration access and caching.
 */

import { useState, useEffect, useCallback } from 'react';
import { settings as settingsApi } from '../services/api';
import type { SystemConfig, SettingsGroup } from '../types';

const CONFIG_CACHE_KEY = 'pharmalert-config-cache';
const CONFIG_CACHE_TTL = 5 * 60 * 1000; // 5 minutes

interface CacheEntry {
  data: SettingsGroup[];
  timestamp: number;
}

function getCachedConfig(): SettingsGroup[] | null {
  try {
    const cached = localStorage.getItem(CONFIG_CACHE_KEY);
    if (!cached) return null;

    const entry: CacheEntry = JSON.parse(cached);
    if (Date.now() - entry.timestamp > CONFIG_CACHE_TTL) {
      localStorage.removeItem(CONFIG_CACHE_KEY);
      return null;
    }

    return entry.data;
  } catch {
    return null;
  }
}

function setCachedConfig(data: SettingsGroup[]) {
  const entry: CacheEntry = { data, timestamp: Date.now() };
  localStorage.setItem(CONFIG_CACHE_KEY, JSON.stringify(entry));
}

export function useSettings(entityId?: number) {
  const [groups, setGroups] = useState<SettingsGroup[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);

  // Load from cache first
  useEffect(() => {
    const cached = getCachedConfig();
    if (cached) {
      setGroups(cached);
    }
  }, []);

  const loadSettings = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const data = await settingsApi.grouped(entityId);
      setGroups(data);
      setCachedConfig(data);
      setIsDirty(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement des paramètres');
      console.error('Failed to load settings:', err);
    } finally {
      setIsLoading(false);
    }
  }, [entityId]);

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  const updateSetting = useCallback(async (key: string, value: string) => {
    try {
      await settingsApi.updateByKey(key, value, entityId);
      setIsDirty(true);

      // Update local state
      setGroups(prev => prev.map(group => ({
        ...group,
        configs: group.configs.map(config =>
          config.key === key ? { ...config, value } : config
        ),
      })));

      // Clear cache
      localStorage.removeItem(CONFIG_CACHE_KEY);
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Erreur lors de la mise à jour');
    }
  }, [entityId]);

  const bulkUpdate = useCallback(async (updates: { key: string; value: string }[]) => {
    try {
      await settingsApi.bulkUpdate(updates, entityId);
      setIsDirty(true);
      await loadSettings();
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Erreur lors de la mise à jour');
    }
  }, [entityId, loadSettings]);

  const getValue = useCallback((key: string): string | undefined => {
    for (const group of groups) {
      const config = group.configs.find(c => c.key === key);
      if (config) return config.value;
    }
    return undefined;
  }, [groups]);

  const getBool = useCallback((key: string, defaultValue = false): boolean => {
    const value = getValue(key);
    if (value === undefined) return defaultValue;
    return value.toLowerCase() === 'true' || value === '1';
  }, [getValue]);

  const getInt = useCallback((key: string, defaultValue = 0): number => {
    const value = getValue(key);
    if (value === undefined) return defaultValue;
    return parseInt(value, 10) || defaultValue;
  }, [getValue]);

  const clearCache = useCallback(() => {
    localStorage.removeItem(CONFIG_CACHE_KEY);
    setIsDirty(true);
  }, []);

  return {
    groups,
    isLoading,
    error,
    isDirty,
    loadSettings,
    updateSetting,
    bulkUpdate,
    getValue,
    getBool,
    getInt,
    clearCache,
  };
}

// ========================
// Public Config Hook (no auth)
// ========================

export function usePublicSettings(entityId?: number) {
  const [config, setConfig] = useState<Record<string, unknown>>({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setIsLoading(true);
        const data = await settingsApi.getPublicGrouped(entityId);

        const flatConfig: Record<string, unknown> = {};
        for (const group of data) {
          for (const item of group.configs) {
            flatConfig[item.key] = item.value;
          }
        }
        setConfig(flatConfig);
      } catch (err) {
        console.error('Failed to load public settings:', err);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [entityId]);

  return { config, isLoading };
}