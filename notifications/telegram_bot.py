import os
import requests
from typing import List, Dict, Any

class TelegramNotifier:
    """Envía notificaciones de vacantes destacadas a Telegram."""

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send_message(self, message: str) -> bool:
        if not self.bot_token or not self.chat_id:
            print("ℹ️ Telegram credentials not found. Skipping notifications.")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            res = requests.post(url, json=payload, timeout=5)
            return res.status_code == 200
        except Exception as e:
            print(f"Error sending Telegram alert: {e}")
            return False

    def notify_top_jobs(self, jobs: List[Dict[str, Any]], min_score: float = 85.0):
        top_jobs = [j for j in jobs if j.get("compatibilidad", 0) >= min_score]
        if not top_jobs:
            return

        msg = f"🔥 <b>Job Hunter AI Alert!</b> 🔥\nSe encontraron {len(top_jobs)} vacantes destacadas:\n\n"
        for j in top_jobs[:5]:
            msg += f"🎯 <b>{j['puesto']}</b> ({j['compatibilidad']}%)\n"
            msg += f"🏢 {j['empresa']} | 📍 {j['modalidad']}\n"
            msg += f"🔗 <a href='{j['url']}'>Ver Oferta</a>\n\n"

        self.send_message(msg)