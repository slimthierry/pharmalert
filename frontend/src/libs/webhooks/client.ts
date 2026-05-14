/**
 * Webhook client for sending PharmAlert notifications to external systems.
 */

import { WebhookEventType, createWebhookPayload } from './events';

export interface WebhookClientConfig {
  urls: string[];
  secret: string;
  timeout?: number;
}

export class WebhookClient {
  private urls: string[];
  private secret: string;
  private timeout: number;

  constructor(config: WebhookClientConfig) {
    this.urls = config.urls;
    this.secret = config.secret;
    this.timeout = config.timeout || 10000;
  }

  /**
   * Send a webhook event to all configured URLs.
   */
  async send(
    eventType: WebhookEventType,
    data: Record<string, unknown>,
  ): Promise<void> {
    const payload = createWebhookPayload(eventType, data);
    const body = JSON.stringify(payload);

    const signature = await this.generateSignature(body);

    const headers = {
      'Content-Type': 'application/json',
      'X-PharmAlert-Event': eventType,
      'X-PharmAlert-Signature': signature,
    };

    const promises = this.urls.map(async (url) => {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const response = await fetch(url, {
          method: 'POST',
          headers,
          body,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          console.error(
            `Webhook failed for ${url}: status=${response.status}`,
          );
        }
      } catch (error) {
        console.error(`Webhook error for ${url}:`, error);
      }
    });

    await Promise.allSettled(promises);
  }

  /**
   * Send a critical interaction alert.
   */
  async sendCriticalInteraction(data: {
    prescription_id?: number;
    patient_ipp: string;
    interactions: unknown[];
  }): Promise<void> {
    await this.send(WebhookEventType.CRITICAL_INTERACTION, data);
  }

  /**
   * Send a missed dose alert.
   */
  async sendMissedDose(data: {
    administration_id: number;
    prescription_id: number;
    patient_ipp: string;
    scheduled_at: string;
  }): Promise<void> {
    await this.send(WebhookEventType.MISSED_DOSE, data);
  }

  /**
   * Send an adverse event notification.
   */
  async sendAdverseEvent(data: {
    event_id: number;
    patient_ipp: string;
    severity: string;
    description: string;
  }): Promise<void> {
    await this.send(WebhookEventType.ADVERSE_EVENT, data);
  }

  private async generateSignature(payload: string): Promise<string> {
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      'raw',
      encoder.encode(this.secret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign'],
    );
    const signatureBuffer = await crypto.subtle.sign(
      'HMAC',
      key,
      encoder.encode(payload),
    );
    return Array.from(new Uint8Array(signatureBuffer))
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');
  }
}
