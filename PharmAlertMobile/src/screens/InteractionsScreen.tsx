import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, RefreshControl, StyleSheet, TouchableOpacity } from 'react-native';
import { api } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import Logo from '../components/Logo';
import type { Interaction, InteractionCheckResponse } from '../types';

const SEVERITY_COLORS: Record<string, string> = {
  minor: '#10B981',
  moderate: '#F59E0B',
  major: '#EF4444',
  contraindicated: '#7C3AED',
};

const SEVERITY_LABELS: Record<string, string> = {
  minor: 'Mineur',
  moderate: 'Modéré',
  major: 'Majeur',
  contraindicated: 'C-I',
};

export default function InteractionsScreen() {
  const { theme } = useTheme();
  const [items, setItems] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  const load = async () => {
    try {
      const res = await api.getInteractions(0, 50);
      setItems(res.items);
      setError(null);
    } catch {
      setError('Impossible de charger les interactions');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { load(); }, []);
  const onRefresh = () => { setRefreshing(true); load(); };

  const toggleSelect = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const renderItem = ({ item }: { item: Interaction }) => {
    const isSelected = selectedIds.includes(item.id);
    const color = SEVERITY_COLORS[item.severity] || '#6B7280';

    return (
      <TouchableOpacity
        style={[
          styles.card,
          { backgroundColor: theme.colors.card },
          isSelected && { borderColor: theme.colors.info, borderWidth: 2 },
        ]}
        onPress={() => toggleSelect(item.id)}
        activeOpacity={0.7}
      >
        <View style={styles.cardHeader}>
          <View style={[styles.severityBadge, { backgroundColor: color }]}>
            <Text style={styles.severityText}>{SEVERITY_LABELS[item.severity] || item.severity}</Text>
          </View>
          <Text style={[styles.selectIndicator, { color: isSelected ? theme.colors.success : theme.colors.textTertiary }]}>
            {isSelected ? '✓' : '+'}
          </Text>
        </View>
        <View style={styles.drugPair}>
          <Text style={[styles.drug, { color: theme.colors.text }]} numberOfLines={1}>
            💊 {item.medication_a_name || `#${item.medication_a_id}`}
          </Text>
          <Text style={styles.drugArrow}>↔</Text>
          <Text style={[styles.drug, { color: theme.colors.text }]} numberOfLines={1}>
            💊 {item.medication_b_name || `#${item.medication_b_id}`}
          </Text>
        </View>
        <Text style={[styles.effect, { color: theme.colors.textSecondary }]} numberOfLines={2}>
          {item.clinical_effect}
        </Text>
        <View style={[styles.recommendationBox, { backgroundColor: theme.dark ? '#1A3A2A' : '#ECFDF5' }]}>
          <Text style={[styles.recommendation, { color: theme.colors.success }]}>{item.recommendation}</Text>
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <View style={[styles.container, { flex: 1, backgroundColor: theme.colors.background }]}>
      {/* ── Header ── */}
      <View style={[styles.screenHeader, { backgroundColor: theme.colors.primary }]}>
        <View style={styles.headerTop}>
          <Logo size="small" />
        </View>
        <Text style={styles.screenTitle}>Interactions</Text>
        <Text style={styles.screenSubtitle}>{items.length} interactions connues</Text>
      </View>

      {/* ── Selection info ── */}
      {selectedIds.length > 0 && (
        <View style={[styles.selectionBar, { backgroundColor: theme.colors.info }]}>
          <Text style={styles.selectionText}>{selectedIds.length} sélectionné(s)</Text>
          <TouchableOpacity onPress={() => setSelectedIds([])}>
            <Text style={styles.clearText}>Tout effacer</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* ── Error ── */}
      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      <FlatList
        data={items}
        keyExtractor={(i) => String(i.id)}
        renderItem={renderItem}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <Text style={[styles.empty, { color: theme.colors.textTertiary }]}>
            {loading ? 'Chargement...' : 'Aucune interaction'}
          </Text>
        }
        contentContainerStyle={{ flexGrow: 1, padding: 16 }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  screenHeader: { padding: 20, paddingTop: 56, paddingBottom: 16 },
  headerTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  screenTitle: { fontSize: 20, fontWeight: 'bold', color: '#fff' },
  screenSubtitle: { fontSize: 12, color: '#93C5FD', marginTop: 2 },
  selectionBar: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 10 },
  selectionText: { color: '#fff', fontSize: 14, fontWeight: '600' },
  clearText: { color: '#fff', fontSize: 13, fontWeight: '600', textDecorationLine: 'underline' },
  errorBanner: { backgroundColor: '#FEE2E2', padding: 10, marginHorizontal: 16, marginTop: 8, borderRadius: 8 },
  errorText: { color: '#DC2626', textAlign: 'center', fontSize: 13 },
  card: { borderRadius: 12, padding: 14, marginBottom: 10, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  severityBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 10 },
  severityText: { color: '#fff', fontSize: 12, fontWeight: '700', textTransform: 'capitalize' },
  selectIndicator: { fontSize: 20, fontWeight: '700' },
  drugPair: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  drug: { flex: 1, fontSize: 14, fontWeight: '600' },
  drugArrow: { fontSize: 16, color: '#EF4444', marginHorizontal: 8 },
  effect: { fontSize: 13, marginBottom: 8 },
  recommendationBox: { borderRadius: 8, padding: 10 },
  recommendation: { fontSize: 12, fontStyle: 'italic' },
  empty: { textAlign: 'center', fontSize: 16, marginTop: 40 },
});
