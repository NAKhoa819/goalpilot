import React from 'react';
import { View, Text, TouchableOpacity, Image } from 'react-native';
import { ChevronRight } from 'lucide-react-native';
import { LiquidGlassView, isLiquidGlassSupported } from '@callstack/liquid-glass';
import { ChatPreview as ChatPreviewType } from '../../coordinator/types';
import { COLORS } from '../../theme';
import { FONT, FONT_BOLD } from '../../utils/fonts';
import styles from './styles';

interface ChatPreviewProps {
  preview: ChatPreviewType;
  onPress?: () => void;
}

const ChatPreview: React.FC<ChatPreviewProps> = ({ preview, onPress }) => {
  const hasUnread = preview.unread_count > 0;

  return (
    <TouchableOpacity
      activeOpacity={0.88}
      onPress={onPress}
    >
      <LiquidGlassView
        effect="clear"
        interactive={true}
        style={[
          styles.container,
          {
            borderWidth: 1.5,
            borderColor: 'rgba(255, 255, 255, 0.25)',
          },
          !isLiquidGlassSupported && { backgroundColor: 'rgba(255,255,255,0.05)' },
        ]}
      >
        <View style={styles.innerPad}>
          <View style={styles.avatarContainer}>
            <Image
              source={require('../../../assets/logo.png')}
              style={styles.avatarImage}
              resizeMode="contain"
            />
            {hasUnread && (
              <View style={styles.unreadBadge}>
                <Text style={styles.unreadText}>
                  {preview.unread_count > 9 ? '9+' : preview.unread_count}
                </Text>
              </View>
            )}
          </View>

          {/* Message Text Block */}
          <View style={styles.textBlock}>
            <View style={styles.nameRow}>
              <Text style={styles.agentName}>GoalPilot Agent</Text>
              <View style={styles.liveChip}>
                <View style={styles.liveDot} />
                <Text style={styles.liveText}>AI</Text>
              </View>
            </View>
            <Text style={styles.lastMessage} numberOfLines={2}>
              {preview.last_message}
            </Text>
          </View>

          {/* Lucide chevron */}
          <View style={styles.chevronWrap}>
            <ChevronRight size={20} color={COLORS.glowViolet} strokeWidth={2.5} />
          </View>
        </View>
      </LiquidGlassView>
    </TouchableOpacity>
  );
};

export default ChatPreview;