import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, RefreshControl, StyleSheet, TouchableOpacity } from 'react-native';
import { api } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import Logo from '../components/Logo';
import type { PatientAllergy } from '../types';

const SEVERITY_COLORS: Record<string, string> = {
  mild: '#10B981',
  moderate: '#F59E0B',
  severe: '#EF4444',
  life_threatening: '#7C3AED',
};

const ALLERGEN_ICONS: Record<string, string> = {
  medication: '💊',
  food: '🍎',
  environmental: '🌿',
  other: '⚠️',
};

export default function AllergiesScreen() {
  const { theme, toggleTheme, themeMode } = useTheme();
  const [items, setItems] = useState<PatientAllergy[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      const res = await api.getAllergies(0, 100);
      setItems(res.items);
      setError(null);
    } catch {
      setError('Impossible de charger les allergies');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { load(); }, []);
  const onRefresh = () => { setRefreshing(true); load(); };
  const themeIcon = themeMode === 'dark' ? '🌙' : themeMode === 'light' ? '☀️' : '💻';

  const renderItem = ({ item }: { item: PatientAllergy }) => (
    <View style={[styles.card, { backgroundColor: theme.colors.card }]}>
      <View style={styles.cardHeader}>
        <Text style={[styles.ipp, { color: theme.colors.text }]}>{item.patient_ipp}</Text>
        <View style={[styles.badge, { backgroundColor: SEVERITY_COLORS[item.severity] || '#6B7280' }]}>
          <Text style={styles.badgeText}>{item.severity}</Text>
        </View>
      </View>
      <View style={styles.allergenRow}>
        <Text style={styles.allergenIcon}>{ALLERGEN_ICONS[item.allergen_type] || '⚠️'}</Text>
        <Text style={[styles.allergenName, { color: '#DC2626' }]}>{item.allergen_name}</Text>
      </View>
      <View style={styles.detailRow}>
        <Text style={[styles.detail, { color: theme.colors.textSecondary }]}>🔴 {item.reaction_type}</Text>
        {item.confirmed && (
          <Text style={[styles.verified, { color: '#059669' }]}>✓ Vérifié</Text>
        )}
      </View>
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
        <Text style={styles.screenTitle}>Allergies</Text>
        <Text style={styles.screenSubtitle}>{items.length} allergies déclarées</Text>
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
            {loading ? 'Chargement...' : 'Aucune allergie'}
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
  errorBanner: { backgroundColor: '#FEE2E2', padding: 10, marginHorizontal: 16, marginTop: 8, borderRadius: 8 },
  errorText: { color: '#DC2626', textAlign: 'center', fontSize: 13 },
  card: { borderRadius: 12, padding: 16, marginBottom: 10, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  ipp: { fontSize: 15, fontWeight: '700' },
  badge: { paddingHorizontal: 10, paddingVertical: 3, borderRadius: 12 },
  badgeText: { color: '#fff', fontSize: 12, fontWeight: '600', textTransform: 'capitalize' },
  allergenRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 6 },
  allergenIcon: { fontSize: 18, marginRight: 8 },
  allergenName: { fontSize: 15, fontWeight: '600', flex: 1 },
  detailRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  detail: { fontSize: 12, textTransform: 'capitalize' },
  verified: { fontSize: 12, fontWeight: '600' },
  empty: { textAlign: 'center', fontSize: 16, marginTop: 40 },
});
