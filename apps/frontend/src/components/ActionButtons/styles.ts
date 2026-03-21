import { StyleSheet, Dimensions } from 'react-native';
import { COLORS } from '../../theme';
import { FONT_BOLD, FONT_EXTRABOLD } from '../../utils/fonts';

const SCREEN_W = Dimensions.get('window').width;
const TOTAL_W  = SCREEN_W * 0.90;
const BTN_W    = (TOTAL_W - 10) * 0.5;

const styles = StyleSheet.create({
  container: {
    width: TOTAL_W,
    alignSelf: 'center',
    marginTop: 10,
  },
  bigRow: { flexDirection: 'row', gap: 10 },

  // overflow: 'visible' cho phép quầng sáng Neon tỏa ra ngoài viền tấm kính
  bigBtn: {
    width: BTN_W,
    borderRadius: 20,
    overflow: 'visible',
  },
  bigBtnCard: {
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    paddingHorizontal: 10,
    gap: 8,
    // backgroundColor và borderWidth được truyền qua inline style từ component
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

  pillRow:  { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 8 },

  // overflow: 'visible' cho nút pill để glow không bị clip
  pillBtn: {
    borderRadius: 16,
    overflow: 'visible',
    // Neon shadow được truyền từ LiquidGlassView inline style
    shadowColor: COLORS.neonYellow,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 15,
    elevation: 2,
  },
  pillInner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 14,
    paddingVertical: 9,
    // backgroundColor xóa — truyền qua inline style (rgba cực trong suốt)
    borderRadius: 16,
    borderWidth: 1,
    // borderColor truyền qua inline style
  },
  pillLabel: {
    fontFamily: FONT_BOLD,
    fontSize: 12,
    color: COLORS.neonYellow,
    letterSpacing: 0.2,
  },
});

export default styles;
