import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated, Easing } from 'react-native';

interface LogoProps {
  size?: 'small' | 'large';
  animated?: boolean;
}

/**
 * Logo pharmALT — Option D : Caducée Minimaliste
 * Symbole médical universel + Branding PharmAlert
 * Compact et élégant
 */
export default function Logo({ size = 'large', animated = false }: LogoProps) {
  const scaleAnim = useRef(new Animated.Value(0.4)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (!animated) return;

    Animated.parallel([
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 55,
        friction: 6,
        delay: 80,
        useNativeDriver: true,
      }),
      Animated.timing(opacityAnim, {
        toValue: 1,
        duration: 500,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
    ]).start();

    const pulse = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.05,
          duration: 2400,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 2400,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    );
    pulse.start();
    return () => pulse.stop();
  }, [animated]);

  const isSmall = size === 'small';
  const S = isSmall ? 44 : 84;  // circle diameter
  const R = S / 2;
  const staffW = isSmall ? 2 : 3.5;
  const staffH = isSmall ? 30 : 56;
  const wingW = isSmall ? 9 : 16;
  const wingH = isSmall ? 6 : 10;

  const animatedStyle = animated
    ? { transform: [{ scale: scaleAnim }, { scale: pulseAnim }], opacity: opacityAnim }
    : undefined;

  return (
    <View style={styles.wrapper}>
      <Animated.View
        style={[
          styles.circle,
          {
            width: S,
            height: S,
            borderRadius: R,
          },
          animatedStyle,
        ]}
      >
        {/* Caduceus staff */}
        <View
          style={[
            styles.staff,
            {
              width: staffW,
              height: staffH,
              borderRadius: staffW / 2,
              top: isSmall ? 4 : 7,
            },
          ]}
        />

        {/* Left wing */}
        <View
          style={[
            styles.wing,
            styles.wingLeft,
            {
              width: wingW,
              height: wingH,
              borderTopLeftRadius: wingW,
              borderBottomLeftRadius: wingW,
              top: isSmall ? 11 : 19,
              left: isSmall ? -wingW + 1 : -wingW + 2,
              transform: [{ rotate: '15deg' }],
            },
          ]}
        />

        {/* Right wing */}
        <View
          style={[
            styles.wing,
            styles.wingRight,
            {
              width: wingW,
              height: wingH,
              borderTopRightRadius: wingW,
              borderBottomRightRadius: wingW,
              top: isSmall ? 11 : 19,
              right: isSmall ? -wingW + 1 : -wingW + 2,
              transform: [{ rotate: '-15deg' }],
            },
          ]}
        />

        {/* Wing mid lines */}
        <View
          style={[
            styles.wingLine,
            {
              width: wingW + 2,
              height: 1,
              top: isSmall ? 14 : 24,
              left: -(wingW / 2) + staffW / 2 + 1,
              backgroundColor: 'rgba(52,211,153,0.5)',
            },
          ]}
        />
        <View
          style={[
            styles.wingLine,
            {
              width: wingW + 2,
              height: 1,
              top: isSmall ? 18 : 30,
              left: -(wingW / 2) + staffW / 2 + 1,
              backgroundColor: 'rgba(52,211,153,0.5)',
            },
          ]}
        />

        {/* Snake body (arc) — approximated with oval */}
        <View
          style={[
            styles.snake,
            {
              width: isSmall ? 12 : 22,
              height: isSmall ? 8 : 14,
              borderRadius: isSmall ? 6 : 10,
              top: isSmall ? staffH - 8 : staffH - 14,
              left: staffW / 2 - (isSmall ? 6 : 11),
              borderColor: '#34D399',
              borderWidth: 1.5,
              borderBottomWidth: 0,
            },
          ]}
        />

        {/* Snake head */}
        <View
          style={[
            styles.snakeHead,
            {
              width: isSmall ? 5 : 8,
              height: isSmall ? 4 : 7,
              borderRadius: isSmall ? 2 : 3,
              top: isSmall ? staffH - 8 : staffH - 13,
              right: -1,
              backgroundColor: '#34D399',
            },
          ]}
        />

        {/* Inner ring */}
        <View
          style={[
            styles.innerRing,
            {
              width: S - 5,
              height: S - 5,
              borderRadius: (S - 5) / 2,
              borderColor: 'rgba(52, 211, 153, 0.15)',
            },
          ]}
        />

        {/* Verified checkmark badge */}
        <View
          style={[
            styles.checkBadge,
            {
              right: isSmall ? -4 : -7,
              bottom: isSmall ? -4 : -7,
              width: isSmall ? 16 : 28,
              height: isSmall ? 16 : 28,
              borderRadius: isSmall ? 8 : 14,
            },
          ]}
        >
          <Text style={[styles.checkText, { fontSize: isSmall ? 8 : 14 }]}>✓</Text>
        </View>
      </Animated.View>

      {/* Brand text */}
      <View style={[styles.brandRow, { marginTop: isSmall ? 5 : 8 }]}>
        <Text
          style={[
            styles.brandPharm,
            { fontSize: isSmall ? 12 : 20, marginRight: isSmall ? 1 : 2 },
          ]}
        >
          pharm
        </Text>
        <Text style={[styles.brandAlt, { fontSize: isSmall ? 12 : 20 }]}>ALT</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    alignItems: 'center',
  },
  circle: {
    position: 'relative',
    backgroundColor: '#0F172A',
    justifyContent: 'flex-start',
    alignItems: 'center',
    overflow: 'visible',
    shadowColor: '#34D399',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.2,
    shadowRadius: 10,
  },
  staff: {
    position: 'absolute',
    backgroundColor: '#34D399',
  },
  wing: {
    position: 'absolute',
    backgroundColor: 'rgba(52, 211, 153, 0.6)',
  },
  wingLeft: {},
  wingRight: {},
  wingLine: {
    position: 'absolute',
  },
  snake: {
    position: 'absolute',
    backgroundColor: 'transparent',
  },
  snakeHead: {
    position: 'absolute',
  },
  innerRing: {
    position: 'absolute',
    borderWidth: 1,
  },
  checkBadge: {
    position: 'absolute',
    backgroundColor: '#10B981',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#0F172A',
    shadowColor: '#10B981',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.5,
    shadowRadius: 4,
    elevation: 4,
  },
  checkText: {
    color: '#fff',
    fontWeight: '700',
  },
  brandRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  brandPharm: {
    fontWeight: '900',
    color: '#34D399',
    letterSpacing: -0.5,
  },
  brandAlt: {
    fontWeight: '900',
    color: '#60A5FA',
    letterSpacing: -0.5,
  },
});