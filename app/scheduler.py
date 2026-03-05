import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, timezone
from app.database import supabase
from app.services.notifications import send_web_push

TW_TZ = timezone(timedelta(hours=8))

async def check_and_notify_users(period: str):
    """
    定期檢查是否該量血壓。如果還沒量，就發送 Web Push。
    period 預期為 'morning' (早晨 06:30) 或 'night' (晚上 22:00)
    """
    print(f"⏰ [Scheduler] Running check for {period} BP logs...")
    now = datetime.now(TW_TZ)
    today_start = datetime.combine(now.date(), datetime.min.time(), tzinfo=TW_TZ).isoformat()
    today_end = datetime.combine(now.date(), datetime.max.time(), tzinfo=TW_TZ).isoformat()

    # 1. 取得所有訂閱了推播的裝置
    subs_res = supabase.table("push_subscriptions").select("*").execute()
    subs = subs_res.data
    
    if not subs:
        print("⏰ [Scheduler] No subscriptions found. Skipping.")
        return

    # 2. 獲取所有使用者今天該時段的紀錄 (過濾出今天有量這時段的人)
    logs_res = supabase.table("health_logs") \
        .select("user_id") \
        .eq("period", period) \
        .gte("created_at", today_start) \
        .lte("created_at", today_end) \
        .execute()
        
    logged_user_ids = {log["user_id"] for log in logs_res.data}
    
    greeting = "早安！昨晚睡得好嗎？" if period == "morning" else "晚安！辛苦了一天，"
    
    count = 0
    # 3. 如果沒量，就依照裝置的 Endpoint 寄送推播
    for sub in subs:
        if sub["user_id"] not in logged_user_ids:
            payload = {
                "title": f"🩺 該量血壓囉！",
                "body": f"{greeting}記得花 5 分鐘量個血壓為健康把關喔！",
                "url": "/"
            }
            subscription_info = {
                "endpoint": sub["endpoint"],
                "keys": {
                    "p256dh": sub["keys_p256dh"],
                    "auth": sub["keys_auth"]
                }
            }
            if send_web_push(subscription_info, payload):
                count += 1
                
    print(f"⏰ [Scheduler] Sent notifications to {count} users for {period}.")

def start_scheduler():
    scheduler = AsyncIOScheduler(timezone=TW_TZ)
    
    # 每天早上 06:30 提醒早晨測量
    scheduler.add_job(
        check_and_notify_users,
        CronTrigger(hour=6, minute=30, timezone=TW_TZ),
        args=["morning"],
        id="morning_reminder",
        replace_existing=True
    )
    
    # 每天晚上 22:00 提醒晚上測量
    scheduler.add_job(
        check_and_notify_users,
        CronTrigger(hour=22, minute=0, timezone=TW_TZ),
        args=["night"],
        id="night_reminder",
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ Notification Scheduler Started (06:30 / 22:00 TW Time)")
