import { StyleSheet, Dimensions } from 'react-native';
import { COLORS } from '../../theme';
import { FONT, FONT_BOLD, FONT_EXTRABOLD } from '../../utils/fonts';
const SCREEN_W = Dimensions.get('window').width;
const TOTAL_W = SCREEN_W - 40;

const styles = StyleSheet.create({
  container: {
    width: TOTAL_W,
    height: 96,
    borderRadius: 24,
    alignSelf: 'center',
    marginTop: 10,
    overflow: 'hidden',
  },
  innerPad: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 18,
    height: '100%',
  },

  // ── Avatar ────────────────────────────────────────────────
  avatarContainer: {
    width: 52,
    height: 52,
    marginRight: 14,
  },
  avatarImage: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: '#FFFFFF',
  },
  unreadBadge: {
    position: 'absolute',
    top: -4,
    right: -4,
    backgroundColor: COLORS.glowPink,
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 4,
    borderWidth: 2,
    borderColor: '#1E1E24',
    elevation: 4,
  },
  unreadText: {
    fontFamily: FONT_BOLD,
    fontSize: 10,
    color: '#FFFFFF',
  },

  // ── Text ─────────────────────────────────────────────────
  textBlock: { flex: 1, justifyContent: 'center' },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
    gap: 8,
  },
  agentName: {
    fontFamily: FONT_EXTRABOLD,
    fontSize: 14,
    color: COLORS.textPrimary,
  },
  liveChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(124,111,247,0.12)',
    paddingHorizontal: 7,
    paddingVertical: 3,
    borderRadius: 99,
    gap: 4,
    borderWidth: 1,
    borderColor: 'rgba(124,111,247,0.3)',
  },
  liveDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: COLORS.glowTeal,
  },
  liveText: {
    fontFamily: FONT_BOLD,
    fontSize: 10,
    color: COLORS.glowViolet,
  },
  lastMessage: {
    fontFamily: FONT,
    fontSize: 13,
    color: COLORS.textSecondary,
    lineHeight: 18,
  },

  // ── Chevron ──────────────────────────────────────────────
  chevronWrap: { width: 24, alignItems: 'center', marginLeft: 4, justifyContent: 'center' },
});

export default styles;