import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  View,
  Text,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  StatusBar,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  Vibration,
  Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Feather } from '@expo/vector-icons';
import * as LocalAuthentication from 'expo-local-authentication';

// NEXUS-Omni Core Endpoint
const API_BASE_URL = 'http://127.0.0.1:8080';

export default function HomeScreen() {
  const [targetUrl, setTargetUrl] = useState('');
  const [intercepts, setIntercepts] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [entropy, setEntropy] = useState(0.1);
  const [status, setStatus] = useState('SOVEREIGN_IDLE');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Kinetic Feedback Loop
  useEffect(() => {
    if (entropy > 0.8) {
      // Snipe Window Heartbeat
      const interval = setInterval(() => {
        Vibration.vibrate(10);
      }, 500);
      return () => clearInterval(interval);
    }
  }, [entropy]);

  const authenticate = async () => {
    const hasHardware = await LocalAuthentication.hasHardwareAsync();
    const isEnrolled = await LocalAuthentication.isEnrolledAsync();

    if (!hasHardware || !isEnrolled) {
      // Fallback for dev environment or non-biometric devices
      setIsAuthenticated(true);
      return;
    }

    const result = await LocalAuthentication.authenticateAsync({
      promptMessage: 'BIO_GHOST_VERIFICATION',
      fallbackLabel: 'Enter Passcode',
    });

    if (result.success) {
      setIsAuthenticated(true);
      Vibration.vibrate(50);
    } else {
      Alert.alert('ACCESS_DENIED', 'Biometric signature mismatch.');
    }
  };

  const handleIntercept = async () => {
    if (!targetUrl.trim()) return;
    
    setIsScanning(true);
    setStatus('MORPHING_PROTOCOL');
    setEntropy(0.4);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/intercept`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: targetUrl.trim() })
      });
      
      if (!response.ok) throw new Error('BYPASS_FAILURE');
      
      const data = await response.json();
      setIntercepts(data);
      setEntropy(0.95);
      setStatus('OMNI_SYNC_LOCKED');
      Vibration.vibrate([0, 50, 20, 50]);
    } catch (error) {
      setStatus('INTERCEPT_ABORTED');
      setEntropy(0.2);
    } finally {
      setIsScanning(false);
    }
  };

  const handleBid = async (item) => {
    if (!isAuthenticated) {
      await authenticate();
      return;
    }

    // Jitter Modulation: 200ms to 1500ms
    const jitter = Math.floor(Math.random() * (1500 - 200 + 1)) + 200;
    setStatus(`BID_JITTER: ${jitter}MS`);

    setTimeout(() => {
      Vibration.vibrate(50);
      Alert.alert('BID_SUBMITTED', `Sovereign bid placed for ${item.title} at ${item.max_bid}`);
      setStatus('OMNI_SYNC_LOCKED');
    }, jitter);
  };

  const InterceptRow = ({ item }) => (
    <View style={[styles.card, { borderLeftColor: item.entropy_level > 0.8 ? '#fbbf24' : '#3b82f6' }]}>
      <View style={styles.cardHeader}>
        <View style={{ flex: 1 }}>
          <Text style={styles.cardTitle}>{item.title}</Text>
          <Text style={styles.cardId}>{item.id} {'// ROI: '} {item.roi_percentage?.toFixed(2)}%</Text>
        </View>
        <View style={styles.priceContainer}>
          <Text style={styles.priceLabel}>MAX_BID_CEILING</Text>
          <Text style={styles.priceValue}>{item.max_bid?.toLocaleString()} <Text style={styles.currency}>USD</Text></Text>
        </View>
      </View>

      <View style={styles.actionRow}>
        <TouchableOpacity style={styles.shredBtn} onPress={() => {
           Vibration.vibrate(5);
           setIntercepts(prev => prev.filter(i => i.id !== item.id));
        }}>
          <Text style={styles.btnText}>SHRED</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.lockBtn, !isAuthenticated && { backgroundColor: '#1e293b' }]}
          onPress={() => handleBid(item)}
        >
          <Text style={styles.btnText}>{isAuthenticated ? 'EXECUTE_BID' : 'UNLOCK_BIO'}</Text>
        </TouchableOpacity>
      </View>

      <View style={[styles.entropyBar, { width: `${item.entropy_level * 100}%`, backgroundColor: item.entropy_level > 0.8 ? '#fbbf24' : '#3b82f6' }]} />
    </View>
  );

  return (
    <KeyboardAvoidingView 
      style={[styles.container, { backgroundColor: `hsl(${210 - (entropy * 165)}, 60%, 4%)` }]}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <StatusBar barStyle="light-content" />
      <SafeAreaView style={styles.safeArea}>

        <View style={styles.header}>
          <View>
            <Text style={styles.headerTitle}>AGENTI</Text>
            <Text style={styles.headerSubtitle}>SOVEREIGN_BIDDING_ENGINE</Text>
          </View>
          <View style={styles.statusBadge}>
            <Text style={styles.statusText}>{status}</Text>
          </View>
        </View>

        <View style={styles.inputSection}>
          <TextInput
            style={styles.input}
            placeholder="AUCTION_URL..."
            placeholderTextColor="#1e293b"
            value={targetUrl}
            onChangeText={setTargetUrl}
            autoCapitalize="none"
          />
          <TouchableOpacity style={styles.initiateBtn} onPress={handleIntercept}>
            {isScanning ? <ActivityIndicator color="#fff" /> : <Feather name="target" size={20} color="#fff" />}
          </TouchableOpacity>
        </View>

        {intercepts.length > 0 ? (
          <FlatList
            data={intercepts}
            keyExtractor={item => item.id}
            contentContainerStyle={styles.list}
            renderItem={({ item }) => <InterceptRow item={item} />}
          />
        ) : (
          <View style={styles.empty}>
            <Feather name="activity" size={48} color="#0f172a" />
            <Text style={styles.emptyText}>AWAITING_COMMAND_INPUT</Text>
          </View>
        )}

        <View style={styles.footer}>
          <Text style={styles.footerText}>RUST_CORE: ONLINE {'//'} GHOST_MODE: ACTIVE</Text>
        </View>
      </SafeAreaView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1 },
  header: {
    padding: 24,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#0f172a',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '900',
    color: '#fff',
    fontStyle: 'italic',
    letterSpacing: -1,
  },
  headerSubtitle: {
    fontSize: 8,
    color: '#334155',
    fontWeight: '900',
    letterSpacing: 2,
    marginTop: 2,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    backgroundColor: '#0f172a',
    borderRadius: 2,
    borderWidth: 1,
    borderColor: '#1e293b',
  },
  statusText: {
    color: '#10b981',
    fontSize: 8,
    fontWeight: '900',
  },
  inputSection: {
    flexDirection: 'row',
    padding: 24,
    gap: 12,
  },
  input: {
    flex: 1,
    height: 50,
    backgroundColor: '#000',
    borderWidth: 1,
    borderColor: '#0f172a',
    paddingHorizontal: 16,
    color: '#fff',
    fontSize: 12,
    fontWeight: '700',
  },
  initiateBtn: {
    width: 50,
    height: 50,
    backgroundColor: '#0f172a',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#1e293b',
  },
  list: { padding: 24 },
  card: {
    backgroundColor: '#000',
    borderWidth: 1,
    borderColor: '#0f172a',
    borderLeftWidth: 4,
    padding: 20,
    marginBottom: 16,
    position: 'relative',
    overflow: 'hidden',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  cardTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '900',
    fontStyle: 'italic',
  },
  cardId: {
    color: '#334155',
    fontSize: 9,
    fontWeight: '800',
    marginTop: 4,
  },
  priceContainer: { alignItems: 'flex-end' },
  priceLabel: { color: '#334155', fontSize: 8, fontWeight: '900', marginBottom: 2 },
  priceValue: { color: '#fff', fontSize: 18, fontWeight: '900' },
  currency: { fontSize: 10, color: '#334155' },
  actionRow: { flexDirection: 'row', gap: 12 },
  shredBtn: {
    flex: 1,
    height: 40,
    borderWidth: 1,
    borderColor: '#1e293b',
    justifyContent: 'center',
    alignItems: 'center',
  },
  lockBtn: {
    flex: 2,
    height: 40,
    backgroundColor: '#2563eb',
    justifyContent: 'center',
    alignItems: 'center',
  },
  btnText: { color: '#fff', fontSize: 10, fontWeight: '900', letterSpacing: 1 },
  entropyBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    height: 2,
    opacity: 0.3,
  },
  empty: { flex: 1, justifyContent: 'center', alignItems: 'center', marginTop: 100 },
  emptyText: { color: '#0f172a', fontSize: 10, fontWeight: '900', marginTop: 20, letterSpacing: 2 },
  footer: {
    padding: 24,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 8,
    color: '#0f172a',
    fontWeight: '900',
    letterSpacing: 1,
  }
});
