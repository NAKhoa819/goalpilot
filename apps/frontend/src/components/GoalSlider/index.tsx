import React, { useCallback, useRef, useState } from 'react';
import {
  NativeScrollEvent,
  NativeSyntheticEvent,
  ScrollView,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { CheckCircle2, AlertTriangle, PauseCircle, Star } from 'lucide-react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { GoalCard } from '../../coordinator/types';
import { GOAL_GRADIENTS } from '../../theme';
import { formatCompactUsd } from '../../utils/currency';
import styles, { CARD_MARGIN, CARD_WIDTH } from './styles';

const STATUS_CONFIG: Record<
  string,
  {
    label: string;
    Icon: React.ComponentType<{ size: number; color: string; strokeWidth: number }>;
  }
> = {
  on_track: {
    label: 'On Track',
    Icon: CheckCircle2,
  },
  at_risk: {
    label: 'At Risk',
    Icon: AlertTriangle,
  },
  completed: {
    label: 'Done',
    Icon: Star,
  },
  paused: {
    label: 'Paused',
    Icon: PauseCircle,
  },
};

const fmtDate = (d: string) => {
  const [y, m, dd] = d.split('-');
  return `${dd}/${m}/${y}`;
};

interface GoalCardItemProps {
  goal: GoalCard;
  index: number;
  isActive: boolean;
  onPress: () => void;
}

const GoalCardItem: React.FC<GoalCardItemProps> = ({ goal, index, isActive, onPress }) => {
  const cfg = STATUS_CONFIG[goal.status] ?? STATUS_CONFIG.on_track;
  const remaining = goal.target_amount - goal.current_saved;
  const pct = Math.min(100, (goal.current_saved / goal.target_amount) * 100);
  const { Icon } = cfg;

  return (
    <TouchableOpacity
      activeOpacity={0.9}
      onPress={onPress}
      style={[styles.cardWrapper, isActive && styles.cardActive]}
    >
      <LinearGradient
        colors={GOAL_GRADIENTS[index % GOAL_GRADIENTS.length] as [string, string, ...string[]]}
        style={styles.cardGradientFull}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.cardHeader}>
          <Text style={styles.goalName} numberOfLines={1}>
            {goal.goal_name}
          </Text>
          <View style={styles.statusBadge}>
            <Icon size={12} color="#000000" strokeWidth={2.5} />
            <Text style={styles.statusText}>{cfg.label}</Text>
          </View>
        </View>

        <View style={styles.amountsRow}>
          <View style={styles.amountBlock}>
            <Text style={styles.amountLabel}>Saved</Text>
            <Text style={styles.amountValue}>{formatCompactUsd(goal.current_saved)}</Text>
          </View>
          <View style={styles.amountDivider} />
          <View style={styles.amountBlock}>
            <Text style={styles.amountLabel}>Target</Text>
            <Text style={styles.amountValue}>{formatCompactUsd(goal.target_amount)}</Text>
          </View>
          <View style={styles.amountDivider} />
          <View style={styles.amountBlock}>
            <Text style={styles.amountLabel}>Remaining</Text>
            <Text style={styles.amountValue}>{formatCompactUsd(remaining)}</Text>
          </View>
        </View>

        <View style={styles.progressBarBg}>
          <View style={[styles.progressBarFill, { width: `${pct}%` }]} />
        </View>
        <View style={styles.progressLabelRow}>
          <Text style={styles.progressPct}>{pct.toFixed(0)}% saved</Text>
          <Text style={styles.targetDate}>By {fmtDate(goal.target_date)}</Text>
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );
};

interface GoalSliderProps {
  goals: GoalCard[];
  activeGoalId: string;
  onSelectGoal: (id: string) => void;
}

const GoalSlider: React.FC<GoalSliderProps> = ({ goals, activeGoalId, onSelectGoal }) => {
  const scrollRef = useRef<ScrollView>(null);
  const [activeDotIndex, setActiveDotIndex] = useState(0);

  const scrollToIndex = useCallback((index: number) => {
    const x = index * (CARD_WIDTH + CARD_MARGIN * 2);
    scrollRef.current?.scrollTo({ x, animated: true });
  }, []);

  const handleScroll = useCallback(
    (e: NativeSyntheticEvent<NativeScrollEvent>) => {
      const x = e.nativeEvent.contentOffset.x;
      const step = CARD_WIDTH + CARD_MARGIN * 2;
      const idx = Math.round(x / step);
      if (idx !== activeDotIndex) setActiveDotIndex(idx);
    },
    [activeDotIndex],
  );

  if (!goals || goals.length === 0) return null;

  return (
    <View style={styles.sliderWrapper}>
      <ScrollView
        ref={scrollRef}
        horizontal
        pagingEnabled={false}
        showsHorizontalScrollIndicator={false}
        decelerationRate="fast"
        snapToInterval={CARD_WIDTH + CARD_MARGIN * 2}
        snapToAlignment="start"
        contentContainerStyle={styles.scrollContent}
        onScroll={handleScroll}
        scrollEventThrottle={16}
      >
        {goals.map((goal, index) => (
          <GoalCardItem
            key={goal.goal_id}
            goal={goal}
            index={index}
            isActive={goal.goal_id === activeGoalId || index === activeDotIndex}
            onPress={() => {
              scrollToIndex(index);
              onSelectGoal(goal.goal_id);
            }}
          />
        ))}
      </ScrollView>

      <View style={styles.dots}>
        {goals.map((_, i) => (
          <TouchableOpacity key={i} onPress={() => scrollToIndex(i)}>
            <View style={[styles.dot, i === activeDotIndex && styles.dotActive]} />
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
};

export default GoalSlider;
