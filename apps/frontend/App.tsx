import React, { useState } from 'react';
import { View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer, DarkTheme } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import {
  useFonts,
  BeVietnamPro_400Regular,
  BeVietnamPro_700Bold,
  BeVietnamPro_800ExtraBold
} from '@expo-google-fonts/be-vietnam-pro';
import { LayoutDashboard, Bot } from 'lucide-react-native';
import DashboardScreen from './src/screens/DashboardScreen';
import AgentScreen from './src/screens/AgentScreen';
import { FONT_BOLD } from './src/utils/fonts';

const Tab = createBottomTabNavigator();

export default function App() {
  const [agentScreenInstance, setAgentScreenInstance] = useState(0);
  const [fontsLoaded] = useFonts({
    BeVietnamPro_400Regular,
    BeVietnamPro_700Bold,
    BeVietnamPro_800ExtraBold,
  });

  if (!fontsLoaded) {
    // Màn hình chờ đen tuyền đúng chuẩn Neon
    return <View style={{ flex: 1, backgroundColor: '#000000' }} />;
  }

  // Ép NavigationContainer dùng nền đen tuyền để không bị chớp trắng
  const NeonTheme = {
    ...DarkTheme,
    colors: {
      ...DarkTheme.colors,
      background: '#000000',
    },
  };

  return (
    // THÊM FLEX: 1 VÀ NỀN ĐEN VÀO ĐÂY ĐỂ TRÁNH BỊ NUỐT CHỮ
    <SafeAreaProvider style={{ flex: 1, backgroundColor: '#000000' }}>
      <NavigationContainer theme={NeonTheme}>
        <Tab.Navigator
          screenOptions={({ route }) => ({
            headerShown: false,
            tabBarStyle: {
              backgroundColor: '#151518',
              borderTopColor: '#333333',
              borderTopWidth: 1,
              height: 64,
              paddingBottom: 10,
              paddingTop: 8,
            },
            tabBarActiveTintColor: '#6bf5ff',
            tabBarInactiveTintColor: '#888888',
            tabBarLabelStyle: {
              fontFamily: FONT_BOLD,
              fontSize: 11,
              marginTop: 2,
            },
            tabBarIcon: ({ color, size, focused }) => {
              if (route.name === 'Dashboard') {
                return (
                  <LayoutDashboard
                    size={size}
                    color={color}
                    strokeWidth={focused ? 2.5 : 2}
                  />
                );
              }
              return (
                <Bot
                  size={size}
                  color={color}
                  strokeWidth={focused ? 2.5 : 2}
                />
              );
            },
          })}
        >
          <Tab.Screen
            name="Dashboard"
            component={DashboardScreen}
            options={{ tabBarLabel: 'Overview' }}
          />
          <Tab.Screen
            name="Agent"
            options={{ tabBarLabel: 'AI Advisor' }}
            listeners={{
              blur: () => setAgentScreenInstance((current) => current + 1),
            }}
          >
            {() => <AgentScreen key={agentScreenInstance} />}
          </Tab.Screen>
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
