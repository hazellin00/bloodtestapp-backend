import os
import json
from pywebpush import webpush, WebPushException
from app.database import supabase

VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_CLAIMS_EMAIL = os.getenv("VAPID_CLAIMS_EMAIL")

def send_web_push(subscription_info, payload):
    if not VAPID_PRIVATE_KEY or not VAPID_CLAIMS_EMAIL:
        print("🚨 Web Push Error: VAPID keys not configured.")
        return False
        
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_CLAIMS_EMAIL}
        )
        return True
    except WebPushException as ex:
        print(f"🚨 Web Push Exception: {repr(ex)}")
        # Mozilla Mozilla/Chrome returns 410 or 404 when user unsubscribed or token rotated.
        if ex.response and ex.response.status_code in [404, 410]:
            print(f"🧹 Subscription {subscription_info.get('endpoint')} expired. Removing from DB.")
            try:
                supabase.table("push_subscriptions").delete().eq("endpoint", subscription_info.get("endpoint")).execute()
            except Exception as dbe:
                print(f"🚨 Failed to delete expired subscription: {dbe}")
        return False
    except Exception as e:
        print(f"🚨 General Push Error: {e}")
        return False
