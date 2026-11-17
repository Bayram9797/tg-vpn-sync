import os
import re
import urllib.request
from datetime import datetime, timezone, timedelta

# 👇 Укажите здесь юзернейм публичного Telegram-канала (без знака @) 👇
CHANNEL_NAME = "happvpn"

def fetch_channel_messages(channel):
    url = f"https://t.me/s/{channel}"
    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        
        # Извлекаем тексты сообщений из веб-версии Telegram
        messages = re.findall(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', html, re.DOTALL)
        
        clean_messages = []
        for msg in messages:
            # Убираем HTML-теги
            clean_text = re.sub(r'<[^>]+>', '', msg)
            clean_text = clean_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            clean_messages.append(clean_text)
            
        return clean_messages
    except Exception as e:
        print(f"❌ Ошибка при чтении канала {channel}: {e}")
        return []

def main():
    msk_tz = timezone(timedelta(hours=3))
    now_msk = datetime.now(msk_tz).strftime("%d.%m.%Y %H:%M")
    
    os.makedirs("subs", exist_ok=True)
    
    print(f"Слушаем канал: {CHANNEL_NAME}...")
    messages = fetch_channel_messages(CHANNEL_NAME)
    
    all_configs = []
    for msg in messages:
        lines = msg.splitlines()
        for line in lines:
            line = line.strip()
            # Ищем строки с популярными VPN протоколами
            if any(line.startswith(proto) for proto in ("vless://", "vmess://", "trojan://", "ss://", "hysteria2://", "tuic://")):
                all_configs.append(line)
    
    # Убираем дубликаты
    unique_configs = []
    for cfg in all_configs:
        if cfg not in unique_configs:
            unique_configs.append(cfg)
            
    if unique_configs:
        header = (
            f"#profile-title: Telegram Sync ({CHANNEL_NAME})\n"
            f"#profile-update-interval: 3\n"
            f"#announce: Обновлено из ТГ: {now_msk} (МСК)\n\n"
        )
        content = header + "\n".join(unique_configs) + "\n"
        
        filepath = os.path.join("subs", "telegram_configs.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Найдено и сохранено ключей: {len(unique_configs)}")
    else:
        print("⚠️ Новых ключей в ленте канала не найдено.")
        header = (
            f"#profile-title: Telegram Sync ({CHANNEL_NAME})\n"
            f"#profile-update-interval: 3\n"
            f"#announce: Проверка от {now_msk} - ключи не найдены\n\n"
        )
        filepath = os.path.join("subs", "telegram_configs.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(header + "vless://placeholder_no_keys_found\n")

    with open("status.txt", "w", encoding="utf-8") as f:
        f.write(f"Last tg sync: {now_msk} MSK\n")

if __name__ == "__main__":
    main()
