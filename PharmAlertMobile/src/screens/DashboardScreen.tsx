import React, { useState, useEffect, useRef } from 'react';
import {
  View, Text, ScrollView, RefreshControl, StyleSheet, TouchableOpacity,
  Animated, Dimensions, Platform
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import Logo from '../components/Logo';
import type { DashboardResponse, SIHStatus } from '../types';

const { width } = Dimensions.get('window');
const CARD_W = (width - 48) / 2;

function AnimatedCard({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const anim = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.spring(anim, {
      toValue: 1,
      delay,
      tension: 60,
      friction: 8,
      useNativeDriver: true,
    }).start();
  }, []);
  return (
    <Animated.View style={{ opacity: anim, transform: [{ scale: anim.interpolate({ inputRange: [0, 1], outputRange: [0.8, 1] }) }] }}>
      {children}
    </Animated.View>
  );
}

function StatCard({ title, value, color, icon, subtitle, warning }: {
  title: string; value: string | number; color: string; icon: string; subtitle?: string; warning?: boolean;
}) {
  const { theme } = useTheme();
  return (
    <View style={[styles.statCard, { backgroundColor: theme.colors.card }]}>
      {warning && (
        <View style={[styles.warningDot, { backgroundColor: color }]} />
      )}
      <View style={[styles.statIconBg, { backgroundColor: color + '20' }]}>
        <Text style={styles.statIcon}>{icon}</Text>
      </View>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
      <Text style={[styles.statTitle, { color: theme.colors.textSecondary }]}>{title}</Text>
      {subtitle && (
        <Text style={[styles.statSubtitle, { color: theme.colors.textTertiary }]}>{subtitle}</Text>
      )}
    </View>
  );
}

function SIHBanner({ status }: { status: SIHStatus | null }) {
  const { theme } = useTheme();
  if (!status) return null;

  const lastSync = status.last_sync
    ? new Date(status.last_sync).toLocaleString('fr-FR', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: 'short' })
    : 'Jamais';

  return (
    <AnimatedCard>
      <TouchableOpacity
        style={[styles.sihBanner, { backgroundColor: status.connected ? '#ECFDF5' : '#FEF2F2', borderColor: status.connected ? '#10B981' : '#EF4444' }]}
        activeOpacity={0.7}
      >
        <View style={styles.sihRow}>
          <View style={[styles.sihDot, { backgroundColor: status.connected ? '#10B981' : '#EF4444' }]} />
          <Text style={[styles.sihLabel, { color: status.connected ? '#065F46' : '#991B1B' }]}>
            {status.connected ? '✓ SIH connecté' : '✗ SIH déconnecté'}
          </Text>
        </View>
        <Text style={[styles.sihDetail, { color: status.connected ? '#059669' : '#DC2626' }]}>
          Dernière sync : {lastSync}
        </Text>
        <View style={styles.sihStats}>
          <Text style={styles.sihChip}>👥 {status.patients_count.toLocaleString()}</Text>
          <Text style={styles.sihChip}>💊 {status.drugs_count.toLocaleString()}</Text>
          <Text style={styles.sihChip}>📋 {status.orders_count}</Text>
        </View>
      </TouchableOpacity>
    </AnimatedCard>
  );
}

function AlertCard({ severity, medA, medB }: {
  severity: string; medA: string; medB: string;
}) {
  const { theme } = useTheme();
  const severityColors: Record<string, string> = {
    minor: '#10B981', moderate: '#F59E0B', major: '#EF4444', contraindicated: '#7C3AED',
  };
  const severityLabels: Record<string, string> = {
    minor: 'Mineur', moderate: 'Modéré', major: 'Majeur', contraindicated: 'C-I',
  };
  const color = severityColors[severity] || '#6B7280';

  return (
    <View style={[styles.alertCard, { backgroundColor: theme.colors.card, borderLeftColor: color }]}>
      <View style={styles.alertTop}>
        <Text style={[styles.alertMeds]} numberOfLines={1}>
          💊 {medA}
        </Text>
        <Text style={styles.alertArrow}>↔</Text>
        <Text style={[styles.alertMeds]} numberOfLines={1}>
          💊 {medB}
        </Text>
      </View>
      <View style={[styles.severityBadge, { backgroundColor: color }]}>
        <Text style={styles.severityText}>{severityLabels[severity] || severity}</Text>
      </View>
    </View>
  );
}

function EmptyState({ icon, message }: { icon: string; message: string }) {
  const { theme } = useTheme();
  return (
    <View style={styles.emptyState}>
      <Text style={styles.emptyIcon}>{icon}</Text>
      <Text style={[styles.emptyText, { color: theme.colors.textTertiary }]}>{message}</Text>
    </View>
  );
}

export default function DashboardScreen() {
  const { user, logout } = useAuth();
  const { theme } = useTheme();
  const navigation = useNavigation<any>();
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [sihStatus, setSihStatus] = useState<SIHStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      const [dash, sih] = await Promise.all([
        api.getDashboard(),
        api.getSIHStatus(),
      ]);
      setData(dash);
      setSihStatus(sih);
      setError(null);
    } catch {
      setError('Impossible de charger les données');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { load(); }, []);

  const onRefresh = () => { setRefreshing(true); load(); };

  if (loading) {
    return (
      <View style={[styles.center, { backgroundColor: theme.colors.background }]}>
        <Logo size="small" animated />
        <Text style={[styles.loadingText, { color: theme.colors.textTertiary }]}>Chargement...</Text>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: theme.colors.background }}>
      {/* ── Header ── */}
      <View style={[styles.header, { backgroundColor: theme.colors.primary }]}>
        <View style={styles.headerTop}>
          <Logo size="small" />
        </View>
        <Text style={styles.greeting}>Bonjour, {user?.name || 'Utilisateur'}</Text>
        <Text style={styles.role}>{(user?.role || 'medecin').charAt(0).toUpperCase() + (user?.role || 'medecin').slice(1)}</Text>
        <Text style={styles.date}>
          {new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}
        </Text>
      </View>

      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={{ flexGrow: 1, padding: 16 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        showsVerticalScrollIndicator={false}
      >
        {/* ── Error ── */}
        {error && (
          <View style={[styles.errorBanner, { backgroundColor: '#FEE2E2' }]}>
            <Text style={[styles.errorText, { color: '#DC2626' }]}>{error}</Text>
          </View>
        )}

        {/* ── SIH Banner ── */}
        <SIHBanner status={sihStatus} />

        {/* ── Stats Grid ── */}
        {data && (
          <>
            <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>📊 Statistiques</Text>
            <View style={styles.statsGrid}>
              <AnimatedCard delay={0}>
                <StatCard
                  title="Validations"
                  value={data.stats.pending_validations}
                  color="#F59E0B"
                  icon="⏳"
                  warning={data.stats.pending_validations > 0}
                />
              </AnimatedCard>
              <AnimatedCard delay={60}>
                <StatCard
                  title="Interactions critiques"
                  value={data.stats.critical_interactions}
                  color="#EF4444"
                  icon="⚠️"
                  warning={data.stats.critical_interactions > 0}
                />
              </AnimatedCard>
              <AnimatedCard delay={120}>
                <StatCard
                  title="Doses manquées"
                  value={data.stats.missed_doses_today}
                  color="#DC2626"
                  icon="❌"
                  warning={data.stats.missed_doses_today > 0}
                />
              </AnimatedCard>
              <AnimatedCard delay={180}>
                <StatCard
                  title="Ordonnances actives"
                  value={data.stats.total_active_prescriptions}
                  color="#2563EB"
                  icon="📋"
                />
              </AnimatedCard>
              <AnimatedCard delay={240}>
                <StatCard
                  title="Patients"
                  value={data.stats.total_patients.toLocaleString()}
                  color="#059669"
                  icon="👥"
                />
              </AnimatedCard>
              <AnimatedCard delay={300}>
                <StatCard
                  title="Conformité"
                  value={`${data.stats.compliance_rate}%`}
                  color="#7C3AED"
                  icon="✅"
                  subtitle="Taux de conformité global"
                />
              </AnimatedCard>
            </View>

            {/* ── Critical Interactions ── */}
            <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>⚠️ Interactions Critiques</Text>
            {data.alerts.critical_interactions.length > 0 ? (
              data.alerts.critical_interactions.map((i) => (
                <AlertCard key={i.id} severity={i.severity} medA={i.medication_a_name || `Drug ${i.medication_a_id}`} medB={i.medication_b_name || `Drug ${i.medication_b_id}`} />
              ))
            ) : (
              <EmptyState icon="✅" message="Aucune interaction critique" />
            )}
          </>
        )}

        {/* ── Quick Nav ── */}
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>🔍 Accès rapide</Text>
        <View style={styles.quickNav}>
          {[
            { label: 'Ordonnances', icon: '📋', screen: 'Prescriptions' },
            { label: 'Médicaments', icon: '💊', screen: 'Medications' },
            { label: 'Interactions', icon: '⚠️', screen: 'Interactions' },
            { label: 'Allergies', icon: '🩹', screen: 'Allergies' },
          ].map((item) => (
            <TouchableOpacity
              key={item.screen}
              style={[styles.quickNavCard, { backgroundColor: theme.colors.card }]}
              onPress={() => navigation.navigate(item.screen as never)}
            >
              <Text style={styles.quickNavIcon}>{item.icon}</Text>
              <Text style={[styles.quickNavLabel, { color: theme.colors.textSecondary }]}>{item.label}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* ── Logout ── */}
        <TouchableOpacity style={[styles.logoutBtn, { backgroundColor: '#FEE2E2' }]} onPress={logout}>
          <Text style={[styles.logoutText, { color: '#DC2626' }]}>Déconnexion</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { fontSize: 16, marginTop: 16 },
  header: { padding: 20, paddingTop: 56, paddingBottom: 24 },
  headerTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  greeting: { fontSize: 24, fontWeight: '800', color: '#fff' },
  role: { fontSize: 14, color: '#93C5FD', marginTop: 2, fontWeight: '600' },
  date: { fontSize: 12, color: '#64748B', marginTop: 8, textTransform: 'capitalize' },
  errorBanner: { borderRadius: 10, padding: 12, marginBottom: 12 },
  errorText: { textAlign: 'center', fontSize: 14, fontWeight: '600' },
  sihBanner: {
    borderRadius: 14, padding: 16, marginBottom: 16,
    borderWidth: 1.5,
  },
  sihRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 4 },
  sihDot: { width: 8, height: 8, borderRadius: 4, marginRight: 8 },
  sihLabel: { fontSize: 15, fontWeight: '700' },
  sihDetail: { fontSize: 12, marginLeft: 16, marginBottom: 8 },
  sihStats: { flexDirection: 'row', gap: 8 },
  sihChip: { fontSize: 12, backgroundColor: 'rgba(0,0,0,0.06)', borderRadius: 6, paddingHorizontal: 8, paddingVertical: 3 },
  sectionTitle: { fontSize: 16, fontWeight: '700', marginBottom: 12, marginTop: 4 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginBottom: 8 },
  statCard: {
    width: CARD_W, borderRadius: 14, padding: 16,
    shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 4, elevation: 2,
    overflow: 'hidden',
  },
  warningDot: { position: 'absolute', top: 0, right: 0, width: 8, height: 8, borderRadius: 4, margin: 10 },
  statIconBg: { width: 36, height: 36, borderRadius: 10, justifyContent: 'center', alignItems: 'center', marginBottom: 8 },
  statIcon: { fontSize: 18 },
  statValue: { fontSize: 26, fontWeight: '800', marginBottom: 2 },
  statTitle: { fontSize: 11, fontWeight: '600' },
  statSubtitle: { fontSize: 10, marginTop: 2 },
  alertCard: {
    borderRadius: 10, padding: 14, marginBottom: 8, borderLeftWidth: 4,
  },
  alertTop: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  alertMeds: { flex: 1, fontSize: 13, fontWeight: '600', color: '#1F2937' },
  alertArrow: { fontSize: 14, color: '#EF4444', marginHorizontal: 8 },
  severityBadge: { alignSelf: 'flex-start', borderRadius: 6, paddingHorizontal: 8, paddingVertical: 3 },
  severityText: { color: '#fff', fontSize: 11, fontWeight: '700', textTransform: 'capitalize' },
  emptyState: { alignItems: 'center', padding: 24, marginBottom: 8 },
  emptyIcon: { fontSize: 32, marginBottom: 8 },
  emptyText: { fontSize: 14 },
  quickNav: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 16 },
  quickNavCard: { width: (width - 42) / 2, borderRadius: 12, padding: 16, alignItems: 'center', shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 },
  quickNavIcon: { fontSize: 28, marginBottom: 6 },
  quickNavLabel: { fontSize: 13, fontWeight: '600' },
  logoutBtn: { borderRadius: 12, padding: 16, alignItems: 'center', marginTop: 8, marginBottom: 32 },
  logoutText: { fontWeight: '600', fontSize: 16 },
});
