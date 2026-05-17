import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated, Easing } from 'react-native';

interface LogoProps {
  size?: 'small' | 'large';
  animated?: boolean;
}

/**
 * Logo pharmALT — Gélule ouverte + branding
 * Design clean, sans fond noir — vert & bleu
 */
export default function Logo({ size = 'large', animated = false }: LogoProps) {
  const scaleAnim = useRef(new Animated.Value(0.3)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (!animated) return;

    Animated.parallel([
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 50,
        friction: 6,
        delay: 60,
        useNativeDriver: true,
      }),
      Animated.timing(opacityAnim, {
        toValue: 1,
        duration: 600,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
    ]).start();

    const pulse = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.07,
          duration: 2600,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 2600,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    );
    pulse.start();
    return () => pulse.stop();
  }, [animated]);

  const isSmall = size === 'small';
  const capsuleW = isSmall ? 50 : 96;
  const capsuleH = isSmall ? 26 : 48;
  const halfW = capsuleW / 2;
  const fontBrand = isSmall ? 13 : 22;
  const badgeSize = isSmall ? 16 : 28;
  const badgeFont = isSmall ? 8 : 14;
  const crossSize = isSmall ? 9 : 16;
  const crossThick = isSmall ? 2.5 : 4;

  const animStyle = animated
    ? { opacity: opacityAnim, transform: [{ scale: Animated.multiply(scaleAnim, pulseAnim) }] }
    : undefined;

  return (
    <View style={styles.wrapper}>
      <Animated.View style={[styles.capsuleWrapper, animStyle]}>
        {/* Glow behind capsule */}
        <View
          style={[
            styles.glow,
            {
              width: capsuleW + 12,
              height: capsuleH + 12,
              borderRadius: (capsuleH + 12) / 2,
            },
          ]}
        />

        {/* Capsule body */}
        <View
          style={[
            styles.capsule,
            {
              width: capsuleW,
              height: capsuleH,
              borderRadius: capsuleH / 2,
            },
          ]}
        >
          {/* Left half — green "pharm" */}
          <View
            style={[
              styles.half,
              styles.halfLeft,
              {
                width: halfW,
                height: capsuleH,
                borderTopLeftRadius: capsuleH / 2,
                borderBottomLeftRadius: capsuleH / 2,
              },
            ]}
          />

          {/* Right half — blue "ALT" */}
          <View
            style={[
              styles.half,
              styles.halfRight,
              {
                width: halfW,
                height: capsuleH,
                borderTopRightRadius: capsuleH / 2,
                borderBottomRightRadius: capsuleH / 2,
              },
            ]}
          />

          {/* Divider line */}
          <View style={[styles.divider, { height: capsuleH * 0.65 }]} />

          {/* Shine */}
          <View
            style={[
              styles.shine,
              {
                width: capsuleW * 0.3,
                height: capsuleH * 0.25,
                top: capsuleH * 0.15,
                left: capsuleW * 0.15,
                borderRadius: capsuleH * 0.12,
              },
            ]}
          />

          {/* Exclamation mark */}
          <View style={[styles.exclWrapper, { height: capsuleH }]}>
            <Text
              style={[
                styles.excl,
                {
                  fontSize: isSmall ? 13 : 24,
                  lineHeight: (isSmall ? 13 : 24) * 1.05,
                },
              ]}
            >
              !
            </Text>
          </View>
        </View>

        {/* Medical cross — top right */}
        <View
          style={[
            styles.cross,
            { top: -crossSize * 0.35, right: -crossSize * 0.35 },
          ]}
        >
          <View
            style={[
              styles.crossH,
              { width: crossSize, height: crossThick, borderRadius: crossThick / 2 },
            ]}
          />
          <View
            style={[
              styles.crossV,
              { width: crossThick, height: crossSize, borderRadius: crossThick / 2 },
            ]}
          />
        </View>

        {/* Verified badge — bottom right */}
        <View
          style={[
            styles.badge,
            {
              width: badgeSize,
              height: badgeSize,
              borderRadius: badgeSize / 2,
              right: -badgeSize * 0.3,
              bottom: -badgeSize * 0.3,
            },
          ]}
        >
          <Text style={[styles.badgeText, { fontSize: badgeFont }]}>✓</Text>
        </View>
      </Animated.View>

      {/* Brand name */}
      <View style={[styles.brandRow, { marginTop: isSmall ? 8 : 12 }]}>
        <Text
          style={[
            styles.brandPharm,
            { fontSize: fontBrand, marginRight: isSmall ? 2 : 3 },
          ]}
        >
          pharm
        </Text>
        <Text style={[styles.brandAlt, { fontSize: fontBrand }]}>ALT</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    alignItems: 'center',
  },
  capsuleWrapper: {
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
  },
  glow: {
    position: 'absolute',
    backgroundColor: 'rgba(52, 211, 153, 0.12)',
    shadowColor: '#34D399',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.2,
    shadowRadius: 16,
  },
  capsule: {
    flexDirection: 'row',
    overflow: 'hidden',
    borderWidth: 0,
    elevation: 0,
  },
  half: {},
  halfLeft: {
    backgroundColor: '#34D399',
  },
  halfRight: {
    backgroundColor: '#60A5FA',
  },
  divider: {
    position: 'absolute',
    left: '50%',
    marginLeft: -0.75,
    width: 1.5,
    top: '17.5%',
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 1,
  },
  shine: {
    position: 'absolute',
    backgroundColor: 'rgba(255,255,255,0.25)',
  },
  exclWrapper: {
    position: 'absolute',
    left: 0,
    right: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  excl: {
    color: '#fff',
    fontWeight: '900',
    textShadowColor: 'rgba(0,0,0,0.2)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
  cross: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
  },
  crossH: {
    position: 'absolute',
    backgroundColor: '#34D399',
  },
  crossV: {
    position: 'absolute',
    backgroundColor: '#34D399',
  },
  badge: {
    position: 'absolute',
    backgroundColor: '#10B981',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2.5,
    borderColor: '#fff',
    shadowColor: '#10B981',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.4,
    shadowRadius: 4,
    elevation: 4,
  },
  badgeText: {
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
