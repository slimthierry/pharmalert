/**
 * Webhook event definitions and utilities for PharmAlert SIH integration.
 */

export enum WebhookEventType {
  CRITICAL_INTERACTION = 'critical_interaction',
  MISSED_DOSE = 'missed_dose',
  ADVERSE_EVENT = 'adverse_event',
}

export interface WebhookPayload {
  event_type: WebhookEventType;
  timestamp: string;
  payload: Record<string, unknown>;
}

/**
 * Create a standardized webhook payload.
 */
export function createWebhookPayload(
  eventType: WebhookEventType,
  data: Record<string, unknown>,
): WebhookPayload {
  return {
    event_type: eventType,
    timestamp: new Date().toISOString(),
    payload: data,
  };
}

/**
 * Verify a webhook signature using HMAC-SHA256.
 * Used by webhook receivers to validate the request authenticity.
 */
export async function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string,
): Promise<boolean> {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const signatureBuffer = await crypto.subtle.sign(
    'HMAC',
    key,
    encoder.encode(payload),
  );
  const expected = Array.from(new Uint8Array(signatureBuffer))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
  return expected === signature;
}
