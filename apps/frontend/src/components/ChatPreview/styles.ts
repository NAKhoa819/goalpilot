import { StyleSheet } from 'react-native';
import { COLORS } from '../../theme';
import { FONT, FONT_BOLD, FONT_EXTRABOLD } from '../../utils/fonts';

const styles = StyleSheet.create({
  // ── Container ────────────────────────────────────────────
  container: {
    borderRadius: 24,
    marginHorizontal: 20,
    overflow: 'hidden',
    shadowColor: '#7C6FF7',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.18,
    shadowRadius: 20,
    elevation: 10,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.07)',
  },
  bgGradient: {
    position: 'absolute',
    top: 0, left: 0, right: 0, bottom: 0,
  },
  innerPad: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 18,
  },

  // ── Avatar ────────────────────────────────────────────────
  avatarWrap: {
    width: 52,
    height: 52,
    borderRadius: 26,
    marginRight: 14,
    shadowColor: '#7C6FF7',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.55,
    shadowRadius: 12,
    elevation: 8,
  },
  avatarImageWrap: {
    flex: 1,
    borderRadius: 26,
    overflow: 'hidden',
    backgroundColor: COLORS.bgCardAlt,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarImage: {
    width: '78%',
    height: '78%',
  },
  unreadBadge: {
    position: 'absolute',
    top: -2,
    right: -2,
    backgroundColor: COLORS.glowPink,
    borderRadius: 10,
    minWidth: 18,
    height: 18,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 3,
    borderWidth: 1.5,
    borderColor: COLORS.bgDark,
  },
  unreadText: {
    fontFamily: FONT_BOLD,
    fontSize: 9,
    color: '#FFFFFF',
  },

  // ── Text ─────────────────────────────────────────────────
  textBlock: { flex: 1 },
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
  chevronWrap: { width: 24, alignItems: 'center', marginLeft: 4 },
});

export default styles;
