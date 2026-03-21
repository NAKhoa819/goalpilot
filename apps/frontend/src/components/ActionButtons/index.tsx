import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { LiquidGlassView } from '@callstack/liquid-glass';
import { Check, X, MoreHorizontal } from 'lucide-react-native';
import { ChatAction } from '../../coordinator/types';
import { COLORS } from '../../theme';
import styles from './styles';

interface ActionButtonsProps {
  actions: ChatAction[];
  onPress: (action: ChatAction) => void;
}

type ButtonVariant = 'plan' | 'accept' | 'reject' | 'default';

function getVariant(type: string): ButtonVariant {
  if (type === 'A' || type === 'B') return 'plan';
  if (type.startsWith('accept')) return 'accept';
  if (type === 'cancel') return 'reject';
  return 'default';
}

/** type is already the letter 'A' or 'B' */
function getPlanLetter(type: string) { return type; }

function getPlanSub(label: string) {
  const m = label.match(/—\s*(.+)/);
  return m ? m[1].trim() : label;
}

const BigButton: React.FC<{ action: ChatAction; onPress: () => void }> = ({ action, onPress }) => {
  const variant = getVariant(action.type);

  if (variant === 'plan') {
    const glowColor = action.type === 'A' ? COLORS.neonCyan : COLORS.neonPurple;
    return (
      <TouchableOpacity
        style={[styles.bigBtn, {
          shadowColor: glowColor,
          shadowOffset: { width: 0, height: 0 },
          shadowOpacity: 0.8,
          shadowRadius: 15,
          elevation: 3,
        }]}
        onPress={onPress}
        activeOpacity={0.78}
      >
        <LiquidGlassView
          effect="clear"
          style={[
            styles.bigBtnCard,
            {
              backgroundColor: 'rgba(255, 255, 255, 0.03)',
              borderWidth: 1,
              borderColor: glowColor,
            },
          ]}
        >
          <Text style={[styles.bigLetter, { color: glowColor }]}>
            {getPlanLetter(action.type)}
          </Text>
          <Text style={[styles.bigBtnSub, { color: COLORS.textSecondary }]}>
            {getPlanSub(action.label)}
          </Text>
        </LiquidGlassView>
      </TouchableOpacity>
    );
  }

  if (variant === 'accept') return (
    <TouchableOpacity
      style={[styles.bigBtn, {
        shadowColor: COLORS.neonYellow,
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.8,
        shadowRadius: 15,
        elevation: 3,
      }]}
      onPress={onPress}
      activeOpacity={0.78}
    >
      <LiquidGlassView
        effect="clear"
        style={[
          styles.bigBtnCard,
          {
            backgroundColor: 'rgba(255, 255, 255, 0.03)',
            borderWidth: 1,
            borderColor: COLORS.neonYellow,
          },
        ]}
      >
        <Check size={26} color={COLORS.neonYellow} strokeWidth={2.5} />
        <Text style={[styles.bigBtnSub, { color: COLORS.textPrimary }]}>Apply plan</Text>
      </LiquidGlassView>
    </TouchableOpacity>
  );

  if (variant === 'reject') return (
    <TouchableOpacity
      style={[styles.bigBtn, {
        shadowColor: COLORS.neonPink,
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.8,
        shadowRadius: 15,
        elevation: 3,
      }]}
      onPress={onPress}
      activeOpacity={0.78}
    >
      <LiquidGlassView
        effect="clear"
        style={[
          styles.bigBtnCard,
          {
            backgroundColor: 'rgba(255, 255, 255, 0.03)',
            borderWidth: 1,
            borderColor: COLORS.neonPink,
          },
        ]}
      >
        <X size={26} color={COLORS.neonPink} strokeWidth={2.5} />
        <Text style={[styles.bigBtnSub, { color: COLORS.textPrimary }]}>Keep current</Text>
      </LiquidGlassView>
    </TouchableOpacity>
  );

  return (
    <TouchableOpacity style={styles.pillBtn} onPress={onPress} activeOpacity={0.8}>
      <LiquidGlassView
        effect="clear"
        style={[
          styles.pillInner,
          {
            backgroundColor: 'rgba(255, 255, 255, 0.03)',
            borderColor: COLORS.neonYellow,
          },
        ]}
      >
        <MoreHorizontal size={14} color={COLORS.neonYellow} strokeWidth={2} />
        <Text style={[styles.pillLabel, { color: COLORS.neonYellow }]}>{action.label}</Text>
      </LiquidGlassView>
    </TouchableOpacity>
  );
};

const ActionButtons: React.FC<ActionButtonsProps> = ({ actions, onPress }) => {
  if (!actions || actions.length === 0) return null;
  const big   = actions.filter(a => getVariant(a.type) !== 'default');
  const extra = actions.filter(a => getVariant(a.type) === 'default');
  return (
    <View style={styles.container}>
      {big.length > 0 && (
        <View style={styles.bigRow}>
          {big.map((a, i) => <BigButton key={a.type + i} action={a} onPress={() => onPress(a)} />)}
        </View>
      )}
      {extra.length > 0 && (
        <View style={styles.pillRow}>
          {extra.map((a, i) => <BigButton key={a.type + i} action={a} onPress={() => onPress(a)} />)}
        </View>
      )}
    </View>
  );
};

export default ActionButtons;
