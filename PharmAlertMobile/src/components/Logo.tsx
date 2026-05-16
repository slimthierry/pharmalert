import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated, Easing } from 'react-native';

interface LogoProps {
  size?: 'small' | 'large';
  animated?: boolean;
}

/**
 * Logo pharmALT — Option C : Gélule avec point d'exclamation
 * Alerte + Identité Pharmaceutique + Interaction médicamenteuse
 * Compacte et mémorable
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
        tension: 60,
        friction: 6,
        delay: 60,
        useNativeDriver: true,
      }),
      Animated.timing(opacityAnim, {
        toValue: 1,
        duration: 450,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
    ]).start();

    const pulse = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.06,
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
  // Capsule dimensions — compacte
  const W = isSmall ? 38 : 72;
  const H = isSmall ? 20 : 38;
  const halfW = W / 2;
  const fontExcl = isSmall ? 11 : 20;

  return (
    <View style={styles.wrapper}>
      {/* Capsule外壳 */}
      <Animated.View
        style={[
          styles.capsuleOuter,
          {
            width: W + 6,
            height: H + 6,
            borderRadius: (H + 6) / 2,
            borderTopLeftRadius: isSmall ? 7 : 12,
            borderBottomLeftRadius: isSmall ? 7 : 12,
            transform: [
              { scale: animated ? scaleAnim : 1 },
              { scale: animated ? pulseAnim : 1 },
            ],
            opacity: animated ? opacityAnim : 1,
          },
        ]}
      >
        {/* Capsule body */}
        <View
          style={[
            styles.capsuleBody,
            {
              width: W,
              height: H,
              borderRadius: H / 2,
              borderTopLeftRadius: isSmall ? 7 : 12,
              borderBottomLeftRadius: isSmall ? 7 : 12,
            },
          ]}
        >
          {/* Half 1 — green "pharm" */}
          <View
            style={[
              styles.capsuleHalf,
              styles.halfLeft,
              {
                width: halfW,
                height: H,
                borderTopLeftRadius: isSmall ? 7 : 12,
                borderBottomLeftRadius: isSmall ? 7 : 12,
              },
            ]}
          />

          {/* Half 2 — blue "ALT" */}
          <View
            style={[
              styles.capsuleHalf,
              styles.halfRight,
              {
                width: halfW,
                height: H,
                borderTopRightRadius: H / 2,
                borderBottomRightRadius: H / 2,
              },
            ]}
          />

          {/* Exclamation mark — center overlay */}
          <View style={[styles.exclWrapper, { height: H }]}>
            <Text
              style={[
                styles.exclText,
                {
                  fontSize: fontExcl,
                  lineHeight: fontExcl * 1.1,
                  top: isSmall ? 1 : 2,
                },
              ]}
            >
              !
            </Text>
          </View>

          {/* Capsule shine */}
          <View
            style={[
              styles.capsuleShine,
              {
                width: isSmall ? 7 : 12,
                height: isSmall ? 3 : 5,
                top: isSmall ? 3 : 6,
                left: isSmall ? 9 : 16,
                borderRadius: (isSmall ? 3 : 5) / 2,
              },
            ]}
          />
        </View>
      </Animated.View>

      {/* Brand text */}
      <View style={[styles.brandRow, { marginTop: isSmall ? 4 : 7 }]}>
        <Text
          style={[
            styles.brandPharm,
            { fontSize: isSmall ? 11 : 18, marginRight: isSmall ? 1 : 2 },
          ]}
        >
          pharm
        </Text>
        <Text style={[styles.brandAlt, { fontSize: isSmall ? 11 : 18 }]}>ALT</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    alignItems: 'center',
  },
  capsuleOuter: {
    position: 'relative',
    backgroundColor: 'rgba(52, 211, 153, 0.08)',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#34D399',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
  },
  capsuleBody: {
    position: 'relative',
    flexDirection: 'row',
    overflow: 'hidden',
  },
  capsuleHalf: {},
  halfLeft: {
    backgroundColor: '#34D399',
  },
  halfRight: {
    backgroundColor: '#60A5FA',
  },
  exclWrapper: {
    position: 'absolute',
    left: 0,
    right: 0,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 2,
  },
  exclText: {
    color: '#fff',
    fontWeight: '900',
    textShadowColor: 'rgba(0,0,0,0.25)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
  capsuleShine: {
    position: 'absolute',
    backgroundColor: 'rgba(255,255,255,0.30)',
    zIndex: 3,
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