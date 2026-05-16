import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Platform,
} from 'react-native';
import * as SecureStore from 'expo-secure-store';
import { getBaseUrl } from '../services/api';

const DEFAULT_URL_IOS = 'http://localhost:9600/api/v1';
const DEFAULT_URL_ANDROID = 'http://10.0.2.2:9600/api/v1';

export default function ServerConfigScreen({ navigation }: { navigation: { goBack: () => void } }) {
  const [url, setUrl] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getBaseUrl().then(setUrl);
  }, []);

  const handleSave = async () => {
    if (!url.trim()) {
      Alert.alert('Erreur', 'URL requise');
      return;
    }
    setSaving(true);
    try {
      await SecureStore.setItemAsync('pharmalert_base_url', url.trim());
      Alert.alert('OK', 'Serveur configuré.\nRedémarrez l\'app.', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    } catch (e) {
      Alert.alert('Erreur', 'Impossible de sauvegarder');
    } finally {
      setSaving(false);
    }
  };

  const reset = async () => {
    const defaultUrl = Platform.OS === 'ios' ? DEFAULT_URL_IOS : DEFAULT_URL_ANDROID;
    setUrl(defaultUrl);
    await SecureStore.setItemAsync('pharmalert_base_url', defaultUrl);
    Alert.alert('OK', 'URL réinitialisée');
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Configuration Serveur</Text>
        <Text style={styles.desc}>
          Entrez l'URL de l'API PharmAlert.
        </Text>

        <TextInput
          style={styles.input}
          value={url}
          onChangeText={setUrl}
          placeholder="http://localhost:9600/api/v1"
          autoCapitalize="none"
          autoCorrect={false}
          keyboardType="url"
        />

        <Text style={styles.hint}>
          iPhone (externe): https://9f6210f6a36df0f0-102-64-167-178.serveousercontent.com/api/v1{'\n'}
          Émulateur Android: http://10.0.2.2:9600/api/v1{'\n'}
          Web: http://localhost:9600/api/v1
        </Text>

        <TouchableOpacity
          style={[styles.button, saving && styles.buttonDisabled]}
          onPress={handleSave}
          disabled={saving}
        >
          <Text style={styles.buttonText}>{saving ? 'Enregistrement...' : 'Enregistrer'}</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.resetBtn} onPress={reset}>
          <Text style={styles.resetText}>Réinitialiser</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4F6', padding: 16, paddingTop: 60 },
  card: { backgroundColor: '#fff', borderRadius: 16, padding: 24, shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 8, elevation: 4 },
  title: { fontSize: 22, fontWeight: '700', color: '#1F2937', marginBottom: 8 },
  desc: { fontSize: 14, color: '#6B7280', marginBottom: 20 },
  input: { backgroundColor: '#F9FAFB', borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 10, padding: 14, fontSize: 15, fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace', color: '#1F2937' },
  hint: { fontSize: 12, color: '#9CA3AF', marginTop: 12, marginBottom: 24, lineHeight: 20 },
  button: { backgroundColor: '#1E40AF', borderRadius: 10, padding: 16, alignItems: 'center' },
  buttonDisabled: { opacity: 0.7 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  resetBtn: { marginTop: 16, alignItems: 'center' },
  resetText: { color: '#6B7280', fontSize: 14 },
});
