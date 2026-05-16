import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, RefreshControl, StyleSheet, TouchableOpacity } from 'react-native';
import { api } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import Logo from '../components/Logo';
import type { Prescription } from '../types';

const STATUS_COLORS: Record<string, string> = {
  active: '#059669',
  completed: '#6B7280',
  suspended: '#F59E0B',
  cancelled: '#DC2626',
};

export default function PrescriptionsScreen() {
  const { theme, toggleTheme, themeMode } = useTheme();
  const [items, setItems] = useState<Prescription[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState<string>('active');
  const [error, setError] = useState<string | null>(null);

  const load = async (status?: string) => {
    try {
      const res = await api.getPrescriptions(0, 50, status);
      setItems(res.items);
      setError(null);
    } catch {
      setError('Impossible de charger les ordonnances');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { load(filter); }, [filter]);

  const onRefresh = () => { setRefreshing(true); load(filter); };
  const themeIcon = themeMode === 'dark' ? '🌙' : themeMode === 'light' ? '☀️' : '💻';

  const filters: Array<{ key: string; label: string }> = [
    { key: 'active', label: 'Actives' },
    { key: 'completed', label: 'Terminées' },
    { key: 'suspended', label: 'Suspendues' },
    { key: 'cancelled', label: 'Annulées' },
  ];

  const renderItem = ({ item }: { item: Prescription }) => (
    <View style={[styles.card, { backgroundColor: theme.colors.card }]}>
      <View style={styles.cardHeader}>
        <View style={styles.patientInfo}>
          <Text style={[styles.patientIpp, { color: theme.colors.text }]}>{item.patient_ipp}</Text>
          {item.patient_name && (
            <Text style={[styles.patientName, { color: theme.colors.textSecondary }]}>{item.patient_name}</Text>
          )}
        </View>
        <View style={[styles.badge, { backgroundColor: STATUS_COLORS[item.status] || '#6B7280' }]}>
          <Text style={styles.badgeText}>{item.status}</Text>
        </View>
      </View>
      <Text style={[styles.medName, { color: theme.colors.info }]}>
        {item.medication_name || `Médicament #${item.medication_id}`}
      </Text>
      <View style={styles.detailRow}>
        <Text style={[styles.detail, { backgroundColor: theme.colors.separator }]}>
          💊 {item.dosage_value} {item.dosage_unit}
        </Text>
        <Text style={[styles.detail, { backgroundColor: theme.colors.separator }]}>📅 {item.frequency}</Text>
        <Text style={[styles.detail, { backgroundColor: theme.colors.separator }]}>💉 {item.route}</Text>
      </View>
      <Text style={[styles.prescriber, { color: theme.colors.textTertiary }]}>
        Par : {item.prescriber_name || `#${item.prescriber_id}`}
      </Text>
    </View>
  );

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      {/* ── Header ── */}
      <View style={[styles.screenHeader, { backgroundColor: theme.colors.primary }]}>
        <View style={styles.headerTop}>
          <Logo size="small" />
          <TouchableOpacity style={styles.themeBtn} onPress={toggleTheme}>
            <Text style={styles.themeBtnText}>{themeIcon}</Text>
          </TouchableOpacity>
        </View>
        <Text style={styles.screenTitle}>Ordonnances</Text>
        <Text style={styles.screenSubtitle}>{items.length} résultats</Text>
      </View>

      {/* ── Filters ── */}
      <View style={[styles.filterRow, { backgroundColor: theme.colors.surface }]}>
        {filters.map((f) => (
          <TouchableOpacity
            key={f.key}
            style={[styles.filterChip, filter === f.key && { backgroundColor: theme.colors.primary }]}
            onPress={() => setFilter(f.key)}
          >
            <Text style={[styles.filterText, { color: filter === f.key ? '#fff' : theme.colors.textSecondary }]}>
              {f.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

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
            {loading ? 'Chargement...' : 'Aucune ordonnance'}
          </Text>
        }
        contentContainerStyle={{ padding: 16 }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  screenHeader: { padding: 20, paddingTop: 56, paddingBottom: 16 },
  headerTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  themeBtn: { width: 40, height: 40, borderRadius: 20, backgroundColor: 'rgba(255,255,255,0.15)', justifyContent: 'center', alignItems: 'center' },
  themeBtnText: { fontSize: 20 },
  screenTitle: { fontSize: 20, fontWeight: 'bold', color: '#fff' },
  screenSubtitle: { fontSize: 12, color: '#93C5FD', marginTop: 2 },
  filterRow: { flexDirection: 'row', padding: 12, gap: 8 },
  filterChip: { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 20, backgroundColor: '#E5E7EB' },
  filterText: { fontSize: 13, fontWeight: '600' },
  errorBanner: { backgroundColor: '#FEE2E2', padding: 10, marginHorizontal: 16, marginTop: 8, borderRadius: 8 },
  errorText: { color: '#DC2626', textAlign: 'center', fontSize: 13 },
  card: { borderRadius: 12, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  patientInfo: { flex: 1 },
  patientIpp: { fontSize: 16, fontWeight: '700' },
  patientName: { fontSize: 12, marginTop: 2 },
  badge: { paddingHorizontal: 10, paddingVertical: 3, borderRadius: 12 },
  badgeText: { color: '#fff', fontSize: 12, fontWeight: '600', textTransform: 'capitalize' },
  medName: { fontSize: 15, fontWeight: '600', marginBottom: 6 },
  detailRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 6 },
  detail: { fontSize: 12, borderRadius: 6, paddingHorizontal: 8, paddingVertical: 3 },
  prescriber: { fontSize: 12, marginTop: 4 },
  empty: { textAlign: 'center', fontSize: 16, marginTop: 40 },
});
