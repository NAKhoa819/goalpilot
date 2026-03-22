import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StatusBar,
  TouchableOpacity,
  ActivityIndicator,
  Modal,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  ImageBackground,
} from 'react-native';
import { PenLine, ScanLine, Images } from 'lucide-react-native';
import { SafeAreaView } from "react-native-safe-area-context";
import GoalSlider from '../../components/GoalSlider';
import FinancialChart from '../../components/FinancialChart';
import ChatPreview from '../../components/ChatPreview';
import AppHeader from '../../components/AppHeader';
import { MOCK_CASH_FLOW } from '../../coordinator/mockData';
import { getDashboard, submitManualEntry, uploadReceipt } from '../../coordinator/dashboardCoordinator';
import type { DashboardData } from '../../coordinator/types';
import { COLORS } from '../../theme';
import { FONT_BOLD, FONT_EXTRABOLD } from '../../utils/fonts';
import styles from './styles';

const ACTION_CONFIG = [
  { bg: COLORS.bgCardAlt, glow: COLORS.neonCyan, Icon: PenLine, label: 'Enter Data' },
  { bg: COLORS.bgCardAlt, glow: COLORS.neonYellow, Icon: ScanLine, label: 'Scan Receipt' },
  { bg: COLORS.bgCardAlt, glow: COLORS.neonPurple, Icon: Images, label: 'Add Library' },
];

const DashboardScreen: React.FC = () => {
  const [activeGoalId, setActiveGoalId] = useState<string | null>(null);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

  // Modal states
  const [entryModalVisible, setEntryModalVisible] = useState(false);
  const [entryType, setEntryType] = useState<'income' | 'expense' | null>(null);
  const [entryAmount, setEntryAmount] = useState('');

  const handleQuickAction = async (label: string) => {
    if (label === 'Enter Data') {
      setEntryType(null);
      setEntryAmount('');
      setEntryModalVisible(true);
    } else if (label === 'Scan Receipt') {
      await uploadReceipt('camera');
    } else if (label === 'Add Library') {
      await uploadReceipt('gallery');
    }
  };

  const handleSubmitManual = async () => {
    if (!entryType || !entryAmount) return;
    await submitManualEntry(entryType, Number(entryAmount));
    setEntryModalVisible(false);
  };

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setIsLoading(true);
        setIsError(false);
        const res = await getDashboard();
        if (res.success && res.data) {
          setDashboardData(res.data);
          setActiveGoalId(res.data.active_goal_id);
        } else {
          setIsError(true);
        }
      } catch (error) {
        setIsError(true);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  if (isLoading) {
    return (
      <SafeAreaView style={[styles.root, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={COLORS.neonCyan} />
      </SafeAreaView>
    );
  }

  if (isError || !dashboardData) {
    return (
      <SafeAreaView style={[styles.root, { justifyContent: 'center', alignItems: 'center' }]}>
        <Text style={{ fontFamily: FONT_BOLD, color: COLORS.textPrimary }}>Error loading dashboard data.</Text>
      </SafeAreaView>
    );
  }

  return (
    <ImageBackground
      source={require('../../../assets/backround-01.png')}
      style={styles.root}
      resizeMode="cover"
    >
      <SafeAreaView style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.6)' }}>
        <StatusBar barStyle="light-content" backgroundColor="#000000" translucent={false} />

        <ScrollView
          style={styles.scroll}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <AppHeader />

          {/* ── Active Goals ─────────────────────────────────── */}
          <View style={styles.sectionRow}>
            <Text style={[styles.sectionTitle, { fontFamily: FONT_EXTRABOLD }]}>Active Goals</Text>
          </View>

          <GoalSlider
            goals={dashboardData.goals}
            activeGoalId={activeGoalId || ''}
            onSelectGoal={setActiveGoalId}
          />

          {/* ── Quick Actions ────────────────────────────────── */}
          <View style={styles.quickActions}>
            {ACTION_CONFIG.map(({ bg, glow, Icon, label }) => (
              <TouchableOpacity
                key={label}
                style={[
                  styles.actionBtn,
                  { backgroundColor: bg, borderColor: glow, borderWidth: 1 }
                ]}
                activeOpacity={0.82}
                onPress={() => handleQuickAction(label)}
              >
                <Icon size={18} color={glow} strokeWidth={2} style={{ marginBottom: 5 }} />
                <Text style={[styles.actionLabel, { fontFamily: FONT_BOLD, color: COLORS.textPrimary }]}>
                  {label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* ── Cash Flow ────────────────────────────────────── */}
          <View style={[styles.sectionRow, { marginTop: 26 }]}>
            <Text style={[styles.sectionTitle, { fontFamily: FONT_EXTRABOLD }]}>Cash Flow</Text>
          </View>
          <FinancialChart data={MOCK_CASH_FLOW.points} title="Weekly Overview" />

          {/* ── AI Advisor ───────────────────────────────────── */}
          <View style={[styles.sectionRow, { marginTop: 26 }]}>
            <Text style={[styles.sectionTitle, { fontFamily: FONT_EXTRABOLD }]}>AI Advisor</Text>
          </View>
          <ChatPreview
            preview={dashboardData.chat_preview}
            onPress={() => console.log('Navigate to Agent tab')}
          />

          <View style={{ height: 32 }} />
        </ScrollView>

        {/* ── Enter Data Modal ─────────────────────────────── */}
        <Modal
          visible={entryModalVisible}
          transparent
          animationType="fade"
          onRequestClose={() => setEntryModalVisible(false)}
        >
          <TouchableOpacity
            style={styles.modalOverlay}
            activeOpacity={1}
            onPress={() => setEntryModalVisible(false)}
          />
          <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            style={styles.modalWrapper}
            pointerEvents="box-none"
          >
            <View style={styles.modalContainer}>
              {!entryType ? (
                <>
                  <Text style={styles.modalTitle}>Select Type</Text>
                  <View style={styles.modalBtnRow}>
                    <TouchableOpacity
                      style={[styles.modalBtn, { backgroundColor: COLORS.bgCardAlt, borderColor: COLORS.neonCyan, borderWidth: 1 }]}
                      onPress={() => setEntryType('income')}
                    >
                      <Text style={[styles.modalBtnText, { color: COLORS.neonCyan }]}>Income</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={[styles.modalBtn, { backgroundColor: COLORS.bgCardAlt, borderColor: COLORS.neonPink, borderWidth: 1 }]}
                      onPress={() => setEntryType('expense')}
                    >
                      <Text style={[styles.modalBtnText, { color: COLORS.neonPink }]}>Expense</Text>
                    </TouchableOpacity>
                  </View>
                </>
              ) : (
                <>
                  <Text style={styles.modalTitle}>Enter Amount</Text>
                  <TextInput
                    style={styles.modalInput}
                    keyboardType="numeric"
                    placeholder="e.g. 500000"
                    value={entryAmount}
                    onChangeText={setEntryAmount}
                    autoFocus
                  />
                  <View style={styles.modalBtnRow}>
                    <TouchableOpacity
                      style={[styles.modalBtn, { backgroundColor: COLORS.neonCyan }]}
                      onPress={handleSubmitManual}
                    >
                      <Text style={[styles.modalBtnText, { color: '#000' }]}>Submit</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={[styles.modalBtn, { backgroundColor: COLORS.border }]}
                      onPress={() => setEntryModalVisible(false)}
                    >
                      <Text style={[styles.modalBtnText, { color: COLORS.textPrimary }]}>Cancel</Text>
                    </TouchableOpacity>
                  </View>
                </>
              )}
            </View>
          </KeyboardAvoidingView>
        </Modal>

      </SafeAreaView>
    </ImageBackground>
  );
};

export default DashboardScreen;
