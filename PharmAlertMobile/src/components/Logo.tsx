import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated, Easing } from 'react-native';

interface LogoProps {
  size?: 'small' | 'large';
  animated?: boolean;
}

/**
 * Logo pharmALT — Option P : Lettre "P" stylisée comme une gélule
 * Branding moderne + Identité Pharmaceutique
 */
export default function Logo({ size = 'large', animated = false }: LogoProps) {
  const scaleAnim = useRef(new Animated.Value(0.5)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (!animated) return;

    // Entrance animation
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

    // Subtle pulse
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
  const W = isSmall ? 40 : 76;
  const H = isSmall ? 44 : 84;
  const halfW = W / 2;

  return (
    <View style={styles.wrapper}>
      {/* P — capsule body */}
      <Animated.View
        style={[
          styles.pContainer,
          {
            width: W,
            height: H,
            borderRadius: isSmall ? 18 : 34,
            borderTopLeftRadius: isSmall ? 10 : 20,
            borderBottomLeftRadius: isSmall ? 10 : 20,
            transform: [
              { scale: animated ? scaleAnim : 1 },
              { scale: animated ? pulseAnim : 1 },
            ],
            opacity: animated ? opacityAnim : 1,
          },
        ]}
      >
        {/* Background */}
        <View style={[styles.pBg, {
          width: W,
          height: H,
          borderRadius: isSmall ? 18 : 34,
          borderTopLeftRadius: isSmall ? 10 : 20,
          borderBottomLeftRadius: isSmall ? 10 : 20,
        }]} />

        {/* Outer glow */}
        <View style={[styles.pGlow, {
          width: W + 8,
          height: H + 8,
          borderRadius: (isSmall ? 18 : 34) + 4,
          borderTopLeftRadius: (isSmall ? 10 : 20) + 4,
          borderBottomLeftRadius: (isSmall ? 10 : 20) + 4,
        }]} />

        {/* Left half — green "pharm" */}
        <View style={[styles.pLeft, {
          width: halfW,
          height: H,
          borderTopLeftRadius: isSmall ? 10 : 20,
          borderBottomLeftRadius: isSmall ? 10 : 20,
        }]} />

        {/* Right half — blue "ALT" */}
        <View style={[styles.pRight, {
          width: halfW,
          height: H,
          borderTopRightRadius: isSmall ? 18 : 34,
          borderBottomRightRadius: isSmall ? 18 : 34,
        }]} />

        {/* Center divider */}
        <View style={[styles.pDivider, { height: H * 0.7, top: H * 0.15 }]} />

        {/* Inner highlight (capsule sheen) */}
        <View style={[styles.pSheen, {
          width: isSmall ? 10 : 18,
          height: isSmall ? 4 : 7,
          top: isSmall ? 8 : 14,
          left: isSmall ? 10 : 18,
        }]} />

        {/* Checkmark badge — bottom right */}
        <View style={[styles.checkBadge, {
          right: isSmall ? -4 : -7,
          bottom: isSmall ? -4 : -7,
          width: isSmall ? 16 : 28,
          height: isSmall ? 16 : 28,
          borderRadius: isSmall ? 8 : 14,
        }]}>
          <Text style={[styles.checkText, { fontSize: isSmall ? 8 : 13 }]}>✓</Text>
        </View>

        {/* Medical cross accent — top right */}
        <View style={[styles.crossAccent, {
          top: isSmall ? 3 : 5,
          right: isSmall ? 3 : 5,
        }]}>
          <View style={[styles.crossH, {
            width: isSmall ? 8 : 14,
            height: isSmall ? 2 : 3,
            borderRadius: 1,
          }]} />
          <View style={[styles.crossV, {
            width: isSmall ? 2 : 3,
            height: isSmall ? 8 : 14,
            borderRadius: 1,
          }]} />
        </View>
      </Animated.View>

      {/* Brand text */}
      <View style={[styles.brandRow, { marginTop: isSmall ? 5 : 8 }]}>
        <Text
          style={[
            styles.brandPharm,
            { fontSize: isSmall ? 12 : 20, marginRight: isSmall ? 1.5 : 2 },
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
  pContainer: {
    position: 'relative',
    overflow: 'visible',
  },
  pBg: {
    position: 'absolute',
    top: 0,
    left: 0,
    backgroundColor: 'transparent',
  },
  pGlow: {
    position: 'absolute',
    top: -4,
    left: -4,
    backgroundColor: 'rgba(52, 211, 153, 0.10)',
    shadowColor: '#34D399',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.25,
    shadowRadius: 10,
  },
  pLeft: {
    position: 'absolute',
    left: 0,
    top: 0,
    backgroundColor: '#34D399',
  },
  pRight: {
    position: 'absolute',
    right: 0,
    top: 0,
    backgroundColor: '#60A5FA',
  },
  pDivider: {
    position: 'absolute',
    left: '50%',
    marginLeft: -0.75,
    width: 1.5,
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: 1,
  },
  pSheen: {
    position: 'absolute',
    backgroundColor: 'rgba(255,255,255,0.28)',
    borderRadius: 4,
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
  crossAccent: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
  },
  crossH: {
    position: 'absolute',
    backgroundColor: 'rgba(255,255,255,0.7)',
  },
  crossV: {
    position: 'absolute',
    backgroundColor: 'rgba(255,255,255,0.7)',
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