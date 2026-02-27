import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)


async def send_webhook(event_type: str, payload: dict) -> None:
    """
    Send a webhook notification to all configured URLs.

    Event types:
    - critical_interaction: Contraindicated or major interaction detected
    - missed_dose: A scheduled dose was missed
    - adverse_event: A serious adverse event was reported
    """
    if not settings.WEBHOOK_URLS:
        return

    event = {
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }

    event_json = json.dumps(event, default=str)

    # Generate HMAC signature
    signature = hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        event_json.encode(),
        hashlib.sha256,
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-PharmAlert-Event": event_type,
        "X-PharmAlert-Signature": signature,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in settings.WEBHOOK_URLS:
            try:
                response = await client.post(url, content=event_json, headers=headers)
                logger.info(
                    f"Webhook sent to {url}: status={response.status_code}, "
                    f"event={event_type}"
                )
            except httpx.RequestError as e:
                logger.error(f"Webhook failed for {url}: {e}")
            except Exception as e:
                logger.error(f"Unexpected webhook error for {url}: {e}")
