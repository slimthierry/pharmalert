import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  Animated,
  Easing,
  Dimensions,
  ScrollView,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import Logo from '../components/Logo';
import * as SecureStore from 'expo-secure-store';

const KEY_BASE_URL = 'pharmalert_base_url';
const DEFAULT_URL = 'http://10.10.1.24:9000/api/v1';

const { height } = Dimensions.get('window');

export default function LoginScreen() {
  const { login } = useAuth();
  const { theme, themeMode, setThemeMode } = useTheme();
  const [email, setEmail] = useState('admin@pharmalert.com');
  const [password, setPassword] = useState('admin123');
  const [loading, setLoading] = useState(false);
  const [serverUrl, setServerUrl] = useState(DEFAULT_URL);
  const [editingUrl, setEditingUrl] = useState(false);

  // Animations
  const blob1Anim = useRef(new Animated.ValueXY({ x: 0, y: 0 })).current;
  const blob2Anim = useRef(new Animated.ValueXY({ x: 0, y: 0 })).current;
  const blob3Anim = useRef(new Animated.ValueXY({ x: 0, y: 0 })).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(30)).current;

  useEffect(() => {
    // Entrance animation
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 600,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
    ]).start();

    // Floating blobs
    const createFloat = (anim: Animated.ValueXY, toX: number, toY: number, duration: number) =>
      Animated.loop(
        Animated.sequence([
          Animated.timing(anim, {
            toValue: { x: toX, y: toY },
            duration,
            easing: Easing.inOut(Easing.sin),
            useNativeDriver: true,
          }),
          Animated.timing(anim, {
            toValue: { x: 0, y: 0 },
            duration,
            easing: Easing.inOut(Easing.sin),
            useNativeDriver: true,
          }),
        ])
      );

    const blob1 = createFloat(blob1Anim, 25, 35, 6000);
    const blob2 = createFloat(blob2Anim, -20, 30, 8000);
    const blob3 = createFloat(blob3Anim, 15, -25, 7000);

    blob1.start();
    blob2.start();
    blob3.start();

    return () => { blob1.stop(); blob2.stop(); blob3.stop(); };
  }, []);

  useEffect(() => {
    loadServerUrl();
  }, []);

  const loadServerUrl = async () => {
    try {
      const stored = await SecureStore.getItemAsync(KEY_BASE_URL);
      if (stored) setServerUrl(stored);
    } catch {}
  };

  const saveServerUrl = async (url: string) => {
    await SecureStore.setItemAsync(KEY_BASE_URL, url);
    setServerUrl(url);
    setEditingUrl(false);
  };

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs');
      return;
    }
    setLoading(true);
    try {
      await login(email.trim(), password);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Erreur de connexion';
      Alert.alert('Échec', msg);
    } finally {
      setLoading(false);
    }
  };

  const cycleTheme = () => {
    const modes: Array<'light' | 'dark' | 'system'> = ['system', 'light', 'dark'];
    const idx = modes.indexOf(themeMode);
    setThemeMode(modes[(idx + 1) % modes.length]);
  };

  const themeLabel = themeMode === 'dark' ? '🌙' : themeMode === 'light' ? '☀️' : '💻';

  return (
    <KeyboardAvoidingView
      style={[styles.container, { backgroundColor: theme.dark ? '#0F172A' : '#1E40AF' }]}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      {/* ── Animated blobs ── */}
      <Animated.View style={[styles.blob, styles.blob1, { transform: blob1Anim.getTranslateTransform() }]} />
      <Animated.View style={[styles.blob, styles.blob2, { transform: blob2Anim.getTranslateTransform() }]} />
      <Animated.View style={[styles.blob, styles.blob3, { transform: blob3Anim.getTranslateTransform() }]} />

      {/* ── Theme toggle ── */}
      <TouchableOpacity style={styles.themeBtn} onPress={cycleTheme}>
        <Text style={styles.themeBtnText}>{themeLabel}</Text>
      </TouchableOpacity>

      {/* ── Scrollable content ── */}
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
        style={{ flex: 1 }}
      >
        <Animated.View
          style={[
            styles.inner,
            { opacity: fadeAnim, transform: [{ translateY: slideAnim }] },
          ]}
        >
          {/* ── Logo ── */}
          <View style={styles.logoWrapper}>
            <Logo size="large" animated />
            <Text style={styles.logoLabel}>pharmALT</Text>
          </View>

          <Text style={[styles.subtitle, { color: theme.dark ? '#94A3B8' : '#BFDBFE' }]}>
            Connexion
          </Text>

          {/* ── Server config ── */}
          <View style={[styles.serverBox, { backgroundColor: theme.dark ? '#1E293B' : '#EFF6FF', borderColor: theme.dark ? '#334155' : '#BFDBFE' }]}>
            <Text style={[styles.serverLabel, { color: theme.dark ? '#60A5FA' : '#3B82F6' }]}>🌐 Serveur</Text>
            {editingUrl ? (
              <View style={styles.serverEditRow}>
                <TextInput
                  style={[styles.serverInput, { backgroundColor: theme.dark ? '#0F172A' : '#fff', color: theme.colors.text, borderColor: '#3B82F6' }]}
                  value={serverUrl}
                  onChangeText={setServerUrl}
                  placeholder="http://10.10.1.24:9000/api/v1"
                  autoCapitalize="none"
                  keyboardType="url"
                  placeholderTextColor={theme.colors.textTertiary}
                />
                <TouchableOpacity style={styles.serverSaveBtn} onPress={() => saveServerUrl(serverUrl)}>
                  <Text style={styles.serverSaveBtnText}>✓</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.serverCancelBtn} onPress={() => { setEditingUrl(false); loadServerUrl(); }}>
                  <Text style={styles.serverCancelBtnText}>✕</Text>
                </TouchableOpacity>
              </View>
            ) : (
              <TouchableOpacity style={styles.serverUrlRow} onPress={() => setEditingUrl(true)}>
                <Text style={[styles.serverUrlText, { color: theme.dark ? '#60A5FA' : '#1E40AF' }]} numberOfLines={1}>
                  {serverUrl}
                </Text>
                <Text style={styles.serverEditIcon}>✏️</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* ── Email ── */}
          <TextInput
            style={[styles.input, { backgroundColor: theme.dark ? '#1E293B' : '#fff', color: theme.colors.text, borderColor: theme.colors.border }]}
            placeholder="Email"
            placeholderTextColor={theme.colors.textTertiary}
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            autoCorrect={false}
          />

          {/* ── Password ── */}
          <TextInput
            style={[styles.input, { backgroundColor: theme.dark ? '#1E293B' : '#fff', color: theme.colors.text, borderColor: theme.colors.border }]}
            placeholder="Mot de passe"
            placeholderTextColor={theme.colors.textTertiary}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />

          {/* ── Login button ── */}
          <TouchableOpacity
            style={[styles.button, { backgroundColor: theme.dark ? '#3B82F6' : '#2563EB' }, loading && styles.buttonDisabled]}
            onPress={handleLogin}
            disabled={loading}
            activeOpacity={0.8}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Se connecter</Text>
            )}
          </TouchableOpacity>

          {/* ── Footer ── */}
          <Text style={[styles.footer, { color: theme.dark ? '#475569' : '#64748B' }]}>
            pharmALT © 2026 — Système d'aide à la décision
          </Text>
        </Animated.View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scrollContent: { flexGrow: 1, justifyContent: 'center', paddingHorizontal: 32 },
  blob: {
    position: 'absolute',
    borderRadius: 999,
    opacity: 0.15,
  },
  blob1: {
    width: 280, height: 280,
    backgroundColor: '#34D399',
    top: -60, left: -80,
  },
  blob2: {
    width: 200, height: 200,
    backgroundColor: '#60A5FA',
    bottom: 80, right: -60,
  },
  blob3: {
    width: 160, height: 160,
    backgroundColor: '#818CF8',
    top: height * 0.3, right: -40,
  },
  themeBtn: {
    position: 'absolute', top: 60, right: 20, zIndex: 10,
    width: 44, height: 44,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 22,
    justifyContent: 'center', alignItems: 'center',
  },
  themeBtnText: { fontSize: 22 },
  inner: { flex: 1, justifyContent: 'center', padding: 32 },
  logoWrapper: { alignItems: 'center', marginBottom: 8 },
  logoLabel: { fontSize: 16, fontWeight: '700', marginTop: 12, letterSpacing: 2 },
  subtitle: { fontSize: 18, textAlign: 'center', marginBottom: 40 },
  input: {
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    marginBottom: 16,
    borderWidth: 1,
  },
  button: {
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 4,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 4,
  },
  buttonDisabled: { opacity: 0.7 },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: '600' },
  footer: { fontSize: 11, textAlign: 'center', marginTop: 32 },
  serverBox: {
    borderRadius: 12,
    padding: 14,
    marginBottom: 24,
    borderWidth: 1,
  },
  serverLabel: { fontSize: 12, fontWeight: '600', marginBottom: 8 },
  serverUrlRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  serverUrlText: { fontSize: 13, fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace', flex: 1 },
  serverEditIcon: { fontSize: 14, marginLeft: 8 },
  serverEditRow: { flexDirection: 'row', alignItems: 'center' },
  serverInput: {
    flex: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 8,
    fontSize: 13,
    borderWidth: 1,
    fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
  },
  serverSaveBtn: {
    marginLeft: 8,
    backgroundColor: '#1E40AF',
    borderRadius: 8,
    width: 36, height: 36,
    alignItems: 'center', justifyContent: 'center',
  },
  serverSaveBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  serverCancelBtn: {
    marginLeft: 6,
    backgroundColor: '#E5E7EB',
    borderRadius: 8,
    width: 36, height: 36,
    alignItems: 'center', justifyContent: 'center',
  },
  serverCancelBtnText: { color: '#6B7280', fontSize: 16, fontWeight: '700' },
});
