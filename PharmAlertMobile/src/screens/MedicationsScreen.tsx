import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, RefreshControl, StyleSheet, TextInput } from 'react-native';
import { api } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import Logo from '../components/Logo';
import type { Medication } from '../types';

export default function MedicationsScreen() {
  const { theme } = useTheme();
  const [items, setItems] = useState<Medication[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [search, setSearch] = useState('');
  const [error, setError] = useState<string | null>(null);

  const load = async (q?: string) => {
    setError(null);
    try {
      const res = await api.getMedications(0, 50, q || undefined);
      setItems(res.items);
    } catch (err) {
      setError('Impossible de charger les médicaments. Tirez pour réessayer.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { load(); }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (search || items.length > 0) {
        load(search || undefined);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const onRefresh = () => { setRefreshing(true); load(search || undefined); };

  const renderItem = ({ item }: { item: Medication }) => (
    <View style={[styles.card, { backgroundColor: theme.colors.card }]}>
      <View style={styles.cardTop}>
        <Text style={[styles.name, { color: theme.colors.text }]}>{item.name}</Text>
        {item.atc_code && (
          <View style={styles.atcBadge}>
            <Text style={styles.atcText}>{item.atc_code}</Text>
          </View>
        )}
      </View>
      {item.dci && <Text style={[styles.dci, { color: '#059669' }]}>DCI: {item.dci}</Text>}
      <View style={styles.tags}>
        <View style={[styles.tag, { backgroundColor: theme.colors.primaryLight }]}>
          <Text style={[styles.tagText, { color: theme.colors.info }]}>{item.form || '—'}</Text>
        </View>
        <View style={[styles.tag, { backgroundColor: theme.colors.primaryLight }]}>
          <Text style={[styles.tagText, { color: theme.colors.info }]}>{item.dosage_unit || '—'}</Text>
        </View>
        {item.manufacturer && (
          <View style={[styles.tag, { backgroundColor: theme.colors.primaryLight }]}>
            <Text style={[styles.tagText, { color: theme.colors.info }]}>{item.manufacturer}</Text>
          </View>
        )}
      </View>
      {item.contraindications?.length > 0 && (
        <View style={[styles.contraBox, { backgroundColor: '#FEF2F2' }]}>
          <Text style={styles.contraIcon}>⚠️</Text>
          <Text style={[styles.contra, { color: '#DC2626' }]} numberOfLines={2}>
            {item.contraindications.slice(0, 3).join(', ')}
            {item.contraindications.length > 3 ? ` +${item.contraindications.length - 3}` : ''}
          </Text>
        </View>
      )}
    </View>
  );

  return (
    <View style={[styles.container, { flex: 1, backgroundColor: theme.colors.background }]}>
      {/* ── Header ── */}
      <View style={[styles.screenHeader, { backgroundColor: theme.colors.primary }]}>
        <View style={styles.headerTop}>
          <Logo size="small" />
        </View>
        <Text style={styles.screenTitle}>Médicaments</Text>
        <Text style={styles.screenSubtitle}>{items.length} résultats</Text>
      </View>

      {/* ── Search ── */}
      <View style={[styles.searchRow, { backgroundColor: theme.colors.surface }]}>
        <TextInput
          style={[styles.searchInput, { backgroundColor: theme.colors.inputBg, color: theme.colors.text }]}
          placeholder="Rechercher un médicament..."
          placeholderTextColor={theme.colors.textTertiary}
          value={search}
          onChangeText={setSearch}
          onSubmitEditing={() => load(search || undefined)}
        />
      </View>

      {/* ── Error ── */}
      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      <FlatList
        data={items}
        keyExtractor={(i) => String(i.id ?? i.name ?? Math.random())}
        renderItem={renderItem}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <Text style={[styles.empty, { color: theme.colors.textTertiary }]}>
            {loading ? 'Chargement...' : error ? '' : 'Aucun médicament trouvé'}
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
  searchRow: { padding: 12 },
  searchInput: { borderRadius: 10, padding: 12, fontSize: 16 },
  errorBanner: { backgroundColor: '#FEE2E2', padding: 10, marginHorizontal: 16, marginTop: 8, borderRadius: 8 },
  errorText: { color: '#DC2626', textAlign: 'center', fontSize: 13 },
  card: { borderRadius: 12, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 },
  cardTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 },
  name: { fontSize: 16, fontWeight: '700', flex: 1 },
  atcBadge: { backgroundColor: '#DBEAFE', borderRadius: 6, paddingHorizontal: 8, paddingVertical: 3, marginLeft: 8 },
  atcText: { fontSize: 11, color: '#2563EB', fontWeight: '700' },
  dci: { fontSize: 13, marginBottom: 8 },
  tags: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  tag: { borderRadius: 6, paddingHorizontal: 8, paddingVertical: 3 },
  tagText: { fontSize: 12, fontWeight: '600' },
  contraBox: { flexDirection: 'row', alignItems: 'flex-start', borderRadius: 8, padding: 10, marginTop: 8 },
  contraIcon: { fontSize: 14, marginRight: 6 },
  contra: { fontSize: 12, flex: 1 },
  empty: { textAlign: 'center', fontSize: 16, marginTop: 40 },
});
