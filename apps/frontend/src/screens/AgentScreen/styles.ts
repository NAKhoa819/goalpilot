import { StyleSheet } from 'react-native';
import { COLORS } from '../../theme';
import { FONT, FONT_BOLD, FONT_EXTRABOLD } from '../../utils/fonts';

const styles = StyleSheet.create({
  // ── Root ─────────────────────────────────────────────────
  root: {
    flex: 1,
    backgroundColor: COLORS.bgDark,
  },
  bgGradient: { display: 'none' },

  // ── Message list ─────────────────────────────────────────
  messageList: { flex: 1 },
  listContent: {
    paddingTop: 8,
    paddingBottom: 16,
  },

  // ── Input bar ────────────────────────────────────────────
  inputBar: {
    fontFamily: FONT,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    gap: 10,
    backgroundColor: 'rgba(21, 21, 24, 0.8)', // Glassmorphism
  },

  // Plus button
  plusBtn: {
    width: 42,
    height: 42,
    borderRadius: 21,
    overflow: 'visible',
    //justifyContent: 'center',
    //alignItems: 'center',
    backgroundColor: 'transparent',
  },

  // Text input
  textInput: {
    flex: 1,
    minHeight: 42,
    maxHeight: 100,
    backgroundColor: COLORS.bgDark,
    borderRadius: 21,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontFamily: FONT,
    fontSize: 14,
    color: COLORS.textPrimary,
    borderWidth: 1,
    borderColor: COLORS.border,
  },

  // Send button
  sendBtn: {
    width: 42,
    height: 42,
    borderRadius: 21,
    overflow: 'visible',
    backgroundColor: 'transparent',
  },
  sendBtnGrad: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },

  // Typing indicator
  typingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 16,
    marginBottom: 6,
    gap: 6,
  },
  typingText: {
    fontFamily: FONT,
    fontSize: 12,
    color: COLORS.textMuted,
    fontStyle: 'italic',
  },

  // ── Bottom Sheet ──────────────────────────────────────────
  sheetOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.8)',
  },
  sheet: {
    backgroundColor: COLORS.bgCard,
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    paddingHorizontal: 24,
    paddingBottom: 36,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },
  sheetHandle: {
    width: 40,
    height: 4,
    borderRadius: 2,
    backgroundColor: 'rgba(255,255,255,0.3)',
    alignSelf: 'center',
    marginBottom: 20,
  },
  sheetTitle: {
    fontFamily: FONT_EXTRABOLD,
    fontSize: 18,
    color: COLORS.textPrimary,
    marginBottom: 24,
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  sheetOptions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 28,
  },
  sheetOption: {
    alignItems: 'center',
    gap: 10,
  },
  sheetOptionGrad: {
    width: 70,
    height: 70,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: COLORS.neonCyan,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 8,
    backgroundColor: 'transparent',
  },
  sheetOptionLabel: {
    fontFamily: FONT_BOLD,
    fontSize: 13,
    color: COLORS.textSecondary,
    letterSpacing: 0.2,
  },
  sheetClose: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.1)',
  },
  sheetCloseText: {
    fontFamily: FONT_BOLD,
    fontSize: 14,
    color: COLORS.textMuted,
  },
});

export default styles;
