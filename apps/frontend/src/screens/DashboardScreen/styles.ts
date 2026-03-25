import { StyleSheet } from 'react-native';
import { COLORS } from '../../theme';
import { FONT_BOLD, FONT_EXTRABOLD } from '../../utils/fonts';

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: COLORS.bgDark,
  },
  scroll: { flex: 1 },
  scrollContent: { paddingBottom: 28 },

  // ── Section labels ───────────────────────────────────────
  sectionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 12,
  },
  sectionTitle: {
    fontFamily: FONT_EXTRABOLD,
    fontSize: 20,
    color: COLORS.textPrimary,
    letterSpacing: 0.2,
    textShadowColor: COLORS.textPrimary,
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 8,
  },
  emptyGoalsCard: {
    marginHorizontal: 20,
    borderRadius: 24,
    paddingHorizontal: 20,
    paddingVertical: 22,
    backgroundColor: COLORS.bgCard,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  emptyGoalsTitle: {
    fontSize: 18,
    color: COLORS.textPrimary,
    marginBottom: 8,
  },
  emptyGoalsBody: {
    fontSize: 13,
    lineHeight: 20,
    color: COLORS.textMuted,
  },

  // ── 3 Flat neon action buttons ─────────────────────────
  quickActions: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginTop: 18,
    gap: 8,
  },
  actionBtn: {
    flex: 1,
    borderRadius: 18,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionLabel: {
    fontFamily: FONT_BOLD,
    fontSize: 10,
    letterSpacing: 0.1,
  },

  // ── Modal ────────────────────────────────────────────────
  modalOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.8)', // Darker background for modal
  },
  modalWrapper: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContainer: {
    width: '85%',
    backgroundColor: COLORS.bgCard,
    borderRadius: 24,
    padding: 24,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  modalTitle: {
    fontFamily: FONT_EXTRABOLD,
    fontSize: 18,
    color: COLORS.textPrimary,
    marginBottom: 20,
    textAlign: 'center',
  },
  modalBtnRow: {
    flexDirection: 'row',
    gap: 12,
  },
  modalBtn: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 16,
    alignItems: 'center',
  },
  modalBtnText: {
    fontFamily: FONT_BOLD,
    fontSize: 14,
  },
  modalInput: {
    backgroundColor: COLORS.bgDark,
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
    fontFamily: FONT_BOLD,
    fontSize: 18,
    color: COLORS.textPrimary,
    marginBottom: 20,
    textAlign: 'center',
  },
});

export default styles;
