import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { FONT_EXTRABOLD } from '../../utils/fonts';

const AppHeader: React.FC<{ subtitle?: string }> = ({ subtitle }) => {
  const insets = useSafeAreaInsets();
  return (
    <View style={[styles.wrap, { paddingTop: insets.top }]}>
      <Text style={styles.logo}>GoalPilot</Text>
      {subtitle ? <Text style={styles.sub}>{subtitle}</Text> : null}
    </View>
  );
};

const styles = StyleSheet.create({
  wrap: {
    alignItems: 'center',
    paddingBottom: 14,
    backgroundColor: '#000000ff',
  },
  logo: {
    fontFamily: FONT_EXTRABOLD,
    fontSize: 24,
    color: '#ffffffff',
    letterSpacing: 0.4,
    textShadowColor: '#ffffffff',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 8,
  },
  sub: {
    fontFamily: FONT_EXTRABOLD,
    fontSize: 10,
    color: '#666666',
    letterSpacing: 1.2,
    marginTop: 3,
    textTransform: 'uppercase',
  },
});

export default AppHeader;
