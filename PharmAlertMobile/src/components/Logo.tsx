import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated, Easing } from 'react-native';

interface LogoProps {
  size?: 'small' | 'large';
  animated?: boolean;
}

export default function Logo({ size = 'large', animated = false }: LogoProps) {
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const shimmerAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (!animated) return;

    // Pulse animation
    const pulse = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.06,
          duration: 1600,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1600,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    );

    // Shimmer sweep
    const shimmer = Animated.loop(
      Animated.timing(shimmerAnim, {
        toValue: 1,
        duration: 3000,
        easing: Easing.linear,
        useNativeDriver: true,
      })
    );

    pulse.start();
    shimmer.start();

    return () => {
      pulse.stop();
      shimmer.stop();
    };
  }, [animated]);

  const isSmall = size === 'small';
  const pillSize = isSmall ? 36 : 72;
  const fontSize = isSmall ? 14 : 28;
  const subFontSize = isSmall ? 9 : 14;
  const pillPadding = isSmall ? 10 : 20;

  const shimmerTranslate = shimmerAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [-pillSize * 2, pillSize * 2],
  });

  return (
    <Animated.View
      style={[
        styles.pill,
        {
          width: pillSize,
          height: pillSize,
          borderRadius: pillSize / 2,
          padding: pillPadding,
          transform: [{ scale: animated ? pulseAnim : 1 }],
        },
      ]}
    >
      {/* Gradient shimmer overlay */}
      {animated && (
        <Animated.View
          style={[
            styles.shimmer,
            {
              width: pillSize * 0.6,
              height: pillSize,
              transform: [{ translateX: shimmerTranslate }],
            },
          ]}
        />
      )}

      <View style={styles.content}>
        <Text
          style={[
            styles.plus,
            { fontSize: isSmall ? 14 : 24, marginBottom: isSmall ? -2 : -4 },
          ]}
        >
          +
        </Text>
        <Text
          style={[
            styles.text,
            { fontSize: fontSize, lineHeight: fontSize * 1.1 },
          ]}
        >
          <Text style={[styles.pharm, { fontSize: subFontSize }]}>pharm</Text>
          <Text style={[styles.alt, { fontSize: subFontSize }]}>ALT</Text>
        </Text>
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  pill: {
    backgroundColor: '#0F172A',
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
    shadowColor: '#34D399',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 8,
  },
  shimmer: {
    position: 'absolute',
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderRadius: 999,
    transform: [{ skewX: '-20deg' }],
  },
  content: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  plus: {
    fontWeight: '200',
    color: '#34D399',
    textAlign: 'center',
  },
  text: {
    fontWeight: '800',
    textAlign: 'center',
  },
  pharm: {
    color: '#34D399', // vert
    fontWeight: '800',
  },
  alt: {
    color: '#60A5FA', // bleu
    fontWeight: '800',
  },
});
