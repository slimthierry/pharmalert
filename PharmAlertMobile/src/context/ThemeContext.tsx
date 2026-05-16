import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useColorScheme } from 'react-native';

interface ThemeColors {
  // Backgrounds
  background: string;
  surface: string;
  surfaceSecondary: string;
  card: string;
  // Text
  text: string;
  textSecondary: string;
  textTertiary: string;
  // Brand
  primary: string;
  primaryLight: string;
  brandGreen: string;
  brandBlue: string;
  // Status
  success: string;
  warning: string;
  error: string;
  info: string;
  // Borders
  border: string;
  separator: string;
  // Misc
  inputBg: string;
  tabBarBg: string;
  tabBarBorder: string;
}

interface Theme {
  dark: boolean;
  colors: ThemeColors;
}

const lightTheme: Theme = {
  dark: false,
  colors: {
    background: '#F3F4F6',
    surface: '#FFFFFF',
    surfaceSecondary: '#F9FAFB',
    card: '#FFFFFF',
    text: '#1F2937',
    textSecondary: '#374151',
    textTertiary: '#9CA3AF',
    primary: '#1E40AF',
    primaryLight: '#EFF6FF',
    brandGreen: '#34D399',
    brandBlue: '#60A5FA',
    success: '#059669',
    warning: '#D97706',
    error: '#DC2626',
    info: '#2563EB',
    border: '#E5E7EB',
    separator: '#F3F4F6',
    inputBg: '#F3F4F6',
    tabBarBg: '#FFFFFF',
    tabBarBorder: '#E5E7EB',
  },
};

const darkTheme: Theme = {
  dark: true,
  colors: {
    background: '#0F172A',
    surface: '#1E293B',
    surfaceSecondary: '#1E293B',
    card: '#1E293B',
    text: '#F1F5F9',
    textSecondary: '#CBD5E1',
    textTertiary: '#64748B',
    primary: '#3B82F6',
    primaryLight: '#1E3A5F',
    brandGreen: '#34D399',
    brandBlue: '#60A5FA',
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
    border: '#334155',
    separator: '#1E293B',
    inputBg: '#0F172A',
    tabBarBg: '#1E293B',
    tabBarBorder: '#334155',
  },
};

interface ThemeContextValue {
  theme: Theme;
  toggleTheme: () => void;
  setThemeMode: (mode: 'light' | 'dark' | 'system') => void;
  themeMode: 'light' | 'dark' | 'system';
}

const ThemeContext = createContext<ThemeContextValue>({
  theme: lightTheme,
  toggleTheme: () => {},
  setThemeMode: () => {},
  themeMode: 'system',
});

export function ThemeProvider({ children }: { children: ReactNode }) {
  const systemColorScheme = useColorScheme();
  const [themeMode, setThemeModeState] = useState<'light' | 'dark' | 'system'>('system');

  useEffect(() => {
    // Persist preference
  }, [themeMode]);

  const resolvedTheme = themeMode === 'system'
    ? (systemColorScheme === 'dark' ? darkTheme : lightTheme)
    : themeMode === 'dark' ? darkTheme : lightTheme;

  const toggleTheme = () => {
    setThemeModeState((prev) =>
      prev === 'light' ? 'dark' : prev === 'dark' ? 'system' : 'light'
    );
  };

  const setThemeMode = (mode: 'light' | 'dark' | 'system') => {
    setThemeModeState(mode);
  };

  return (
    <ThemeContext.Provider value={{ theme: resolvedTheme, toggleTheme, setThemeMode, themeMode }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
