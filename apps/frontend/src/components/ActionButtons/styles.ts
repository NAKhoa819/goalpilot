import { StyleSheet, Dimensions } from 'react-native';
import { COLORS } from '../../theme';
import { FONT_BOLD, FONT_EXTRABOLD } from '../../utils/fonts';

const SCREEN_W = Dimensions.get('window').width;
const TOTAL_W = SCREEN_W * 0.90;
const BTN_W = (TOTAL_W - 10) * 0.5;

const styles = StyleSheet.create({
  container: {
    width: TOTAL_W,
    alignSelf: 'center',
    marginTop: 10,
  },
  bigRow: { flexDirection: 'row', gap: 10 },
  bigBtn: {
    width: BTN_W,
    borderRadius: 20,
    overflow: 'hidden',
  },
  bigBtnCard: {
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    paddingHorizontal: 10,
    gap: 8,
    borderWidth: 1,
  },
  bigLetter: {
    fontFamily: FONT_EXTRABOLD,
    fontSize: 24,
    lineHeight: 30,
  },
  bigBtnSub: {
    fontFamily: FONT_BOLD,
    fontSize: 11,
    textAlign: 'center',
    paddingHorizontal: 4,
  },
  pillRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 8 },
  pillBtn: { borderRadius: 16, overflow: 'hidden' },
  pillInner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 14,
    paddingVertical: 9,
    backgroundColor: COLORS.bgCardAlt,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: COLORS.neonYellow,
    shadowColor: COLORS.neonYellow,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 5,
    elevation: 2,
  },
  pillLabel: {
    fontFamily: FONT_BOLD,
    fontSize: 12,
    color: COLORS.neonYellow,
    letterSpacing: 0.2,
  },
});

export default styles;

