/**
 * Settings Page
 *
 * Admin interface for managing system configuration.
 */

import { useState, useEffect } from 'react';
import {
  Settings,
  Save,
  RefreshCw,
  AlertCircle,
  Check,
  Shield,
  Link,
  Bell,
  Stethoscope,
  CreditCard,
  Cog,
  Building2,
  ChevronDown,
  ChevronUp,
  Eye,
  EyeOff,
} from 'lucide-react';
import { settings as settingsApi } from '../services/api';
import { useSettings } from '../hooks/useSettings';
import type { SettingsGroup, SystemConfig } from '../types';

const GROUP_ICONS: Record<string, React.ElementType> = {
  branding: Building2,
  integrations: Link,
  security: Shield,
  notifications: Bell,
  medical: Stethoscope,
  billing: CreditCard,
  general: Cog,
};

const GROUP_COLORS: Record<string, string> = {
  branding: 'bg-purple-100 text-purple-600',
  integrations: 'bg-blue-100 text-blue-600',
  security: 'bg-red-100 text-red-600',
  notifications: 'bg-yellow-100 text-yellow-600',
  medical: 'bg-green-100 text-green-600',
  billing: 'bg-indigo-100 text-indigo-600',
  general: 'bg-gray-100 text-gray-600',
};

export default function SettingsPage() {
  const { groups, isLoading, error, isDirty, updateSetting, bulkUpdate, loadSettings, clearCache } = useSettings();
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(['branding', 'general']));
  const [editedValues, setEditedValues] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [showSecret, setShowSecret] = useState<Set<string>>(new Set());
  const [saveSuccess, setSaveSuccess] = useState(false);

  const toggleGroup = (groupKey: string) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(groupKey)) {
      newExpanded.delete(groupKey);
    } else {
      newExpanded.add(groupKey);
    }
    setExpandedGroups(newExpanded);
  };

  const handleValueChange = (config: SystemConfig, value: string) => {
    setEditedValues(prev => ({
      ...prev,
      [config.key]: value,
    }));
  };

  const getDisplayValue = (config: SystemConfig): string => {
    if (editedValues[config.key] !== undefined) {
      return editedValues[config.key];
    }
    return config.value || '';
  };

  const hasChanges = Object.keys(editedValues).length > 0;

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setSaveSuccess(false);

      const updates = Object.entries(editedValues).map(([key, value]) => ({
        key,
        value,
      }));

      await bulkUpdate(updates);
      setEditedValues({});
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Erreur lors de la sauvegarde');
    } finally {
      setIsSaving(false);
    }
  };

  const handleSeed = async () => {
    try {
      if (!confirm('Créer les configurations par défaut ?')) return;
      await settingsApi.seed();
      await loadSettings();
      alert('Configurations créées avec succès');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Erreur');
    }
  };

  const renderInput = (config: SystemConfig) => {
    const value = getDisplayValue(config);
    const isSecret = config.is_secret;
    const showValue = showSecret.has(config.key);

    const baseInputClass = "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm";

    switch (config.value_type) {
      case 'boolean':
        return (
          <label className="flex items-center gap-2 cursor-pointer">
            <div className="relative">
              <input
                type="checkbox"
                checked={value === 'true'}
                onChange={e => handleValueChange(config, e.target.checked ? 'true' : 'false')}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:bg-blue-600 transition-colors" />
              <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full peer-checked:translate-x-5 transition-transform" />
            </div>
            <span className="text-sm text-gray-600">
              {value === 'true' ? 'Activé' : 'Désactivé'}
            </span>
          </label>
        );

      case 'color':
        return (
          <div className="flex items-center gap-2">
            <input
              type="color"
              value={value || '#3B82F6'}
              onChange={e => handleValueChange(config, e.target.value)}
              className="w-10 h-10 rounded cursor-pointer border-0"
            />
            <input
              type="text"
              value={value}
              onChange={e => handleValueChange(config, e.target.value)}
              className={baseInputClass}
              placeholder="#3B82F6"
            />
          </div>
        );

      case 'integer':
      case 'float':
        return (
          <input
            type="number"
            value={value}
            onChange={e => handleValueChange(config, e.target.value)}
            className={baseInputClass}
            step={config.value_type === 'float' ? '0.01' : '1'}
          />
        );

      case 'url':
        return (
          <input
            type="url"
            value={value}
            onChange={e => handleValueChange(config, e.target.value)}
            className={baseInputClass}
            placeholder="https://..."
          />
        );

      case 'email':
        return (
          <input
            type="email"
            value={value}
            onChange={e => handleValueChange(config, e.target.value)}
            className={baseInputClass}
            placeholder="email@example.com"
          />
        );

      default:
        if (config.choices) {
          try {
            const choices = JSON.parse(config.choices);
            return (
              <select
                value={value}
                onChange={e => handleValueChange(config, e.target.value)}
                className={baseInputClass}
              >
                <option value="">— Choisir —</option>
                {choices.map((choice: string) => (
                  <option key={choice} value={choice}>
                    {choice}
                  </option>
                ))}
              </select>
            );
          } catch {
            // Fall through to text input
          }
        }

        if (isSecret) {
          return (
            <div className="relative">
              <input
                type={showValue ? 'text' : 'password'}
                value={value}
                onChange={e => handleValueChange(config, e.target.value)}
                className={baseInputClass + ' pr-10'}
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => {
                  const newShow = new Set(showSecret);
                  if (newShow.has(config.key)) {
                    newShow.delete(config.key);
                  } else {
                    newShow.add(config.key);
                  }
                  setShowSecret(newShow);
                }}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600"
              >
                {showValue ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          );
        }

        return (
          <textarea
            value={value}
            onChange={e => handleValueChange(config, e.target.value)}
            className={baseInputClass}
            rows={2}
            placeholder="Valeur..."
          />
        );
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Settings className="w-7 h-7" />
            Paramètres Système
          </h1>
          <p className="text-gray-500 mt-1">
            Configurez l'application, les intégrations et les paramètres de sécurité
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleSeed}
            className="px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Initialiser
          </button>
          {hasChanges && (
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {isSaving ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : saveSuccess ? (
                <Check className="w-4 h-4" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              Enregistrer
            </button>
          )}
        </div>
      </div>

      {/* Success Banner */}
      {saveSuccess && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2 text-green-700">
          <Check className="w-5 h-5" />
          Paramètres enregistrés avec succès
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      {/* Dirty Banner */}
      {hasChanges && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center gap-2 text-yellow-700">
          <AlertCircle className="w-5 h-5" />
          Modifications non enregistrées — cliquez sur "Enregistrer" pour les appliquer
        </div>
      )}

      {/* Settings Groups */}
      {groups.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Settings className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun groupe de paramètres</h3>
          <p className="text-gray-500 mb-4">
            Cliquez sur "Initialiser" pour créer les paramètres par défaut
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {groups.map(group => {
            const Icon = GROUP_ICONS[group.group] || Settings;
            const colorClass = GROUP_COLORS[group.group] || 'bg-gray-100 text-gray-600';
            const isExpanded = expandedGroups.has(group.group);

            return (
              <div key={group.group} className="bg-white rounded-lg shadow overflow-hidden">
                {/* Group Header */}
                <button
                  onClick={() => toggleGroup(group.group)}
                  className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colorClass}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="text-left">
                      <h3 className="font-semibold text-gray-900">{group.group_name}</h3>
                      <p className="text-sm text-gray-500">
                        {group.configs.length} paramètre{group.configs.length > 1 ? 's' : ''}
                      </p>
                    </div>
                  </div>
                  {isExpanded ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </button>

                {/* Group Content */}
                {isExpanded && (
                  <div className="border-t">
                    <div className="divide-y">
                      {group.configs.map(config => (
                        <div key={config.key} className="px-6 py-4 grid grid-cols-3 gap-4 items-center">
                          <div>
                            <label className="block text-sm font-medium text-gray-700">
                              {config.display_name || config.key}
                            </label>
                            {config.description && (
                              <p className="text-xs text-gray-500 mt-0.5">{config.description}</p>
                            )}
                          </div>
                          <div className="col-span-2">
                            {renderInput(config)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}