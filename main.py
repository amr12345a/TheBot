from telethon.sync import TelegramClient
import requests
import time

# Use the numeric peer ID or username of your Telegram channel
channel_peer_id = "hdhndxj"

endpoint_url = 'https://restforwarder.onrender.com/items'
poll_interval = 60  # seconds between each fetch
symbol_ids_msg = {}

# === Helper Functions ===
api_id = 6284107
api_hash = "376f444df0fcadd27458653b3f92ed6a"
api_token = "7983219041:AAFX_Lqbag0dauUz2YxSEwl6x2tGuv6OzeQ"
def fetch_data(url: str) -> list:
    """
    Fetch raw text from the endpoint and return a parsed list of signals.
    """
    raw = requests.get(url, headers={"Content-Type": "application/json"}).text
    # Remove stray commas in numeric positions (e.g. "1,23" -> "123")
    s = str(raw)
    for i in range(len(s) - 2):
        if s[i+1] == "," and s[i].isdigit() and s[i+2].isdigit():
            s = s[:i+1] + s[i+2:]
    try:
        data = eval(s.replace("true", "True").replace("false", "False").replace("null", "None"))
        if isinstance(data, list):
            return data
        print("Unexpected data format:", data)
    except Exception as e:
        print("Failed to parse data:", e)
    return []


def format_signal(item: dict) -> str:
    """
    صيغ الإشارة بالشكل المطلوب:
    - بيع (put) أو شراء (call)
    - سهم مع تسمية الهاشتاج
    - السعر الحالي
    - هدف أول
    - هدف ثاني
    - إشارة تحقق الأهداف
    """
    achieved1 = item.get('Achieved1', False)
    achieved2 = item.get('Achieved2', False)
    parts = []
    try:
        if not achieved1 and not achieved2:
            typ = item.get('Type', '')  # 'put' أو 'call'
            symbol = item.get('Pair', '').upper().replace('.A', '')  # مثل 'LULU' أو 'AAPL'
            current_price = item.get('Price', item.get('EntryPrice', ''))
            tp1 = item.get('TakeProfit1') or item.get('TP1')
            tp2 = item.get('TakeProfit2') or item.get('TP2')
            # Flags for achieved targets
            

            # اختيار رمز الإشارة
            icon = '🔴' if typ.lower() == 'put' else '🟢'
            kind = 'فرصة بيعية' if typ.lower() == 'put' else 'فرص شرائية'

            parts = [f"{kind} {icon}",
                    f"النوع: {typ}",
                    f"سهم - #{symbol}",
                    f"سعر السهم الحالي - {current_price}",
                    f"{icon} هدف اول - {tp1}",
                    f"{icon} هدف ثاني - {tp2}"]

        # إضافة حالة التحقيق إن وجدت
        elif achieved2:
            parts.append("تم تحقيق الهدف الاول ✅")
        elif achieved1:
            parts.append("تم تحقيق الهدف الثاني ✅")

        return "\n".join(parts)
    except Exception as e:
        print(f"Error formatting signal: {e}")
        return "خطأ في تنسيق الإشارة"
# === Main Flow ===

def main():
    client = TelegramClient('client22', api_id, api_hash)
    client.start(bot_token=api_token)

    history = fetch_data(endpoint_url)
    print("Signal bot started and connected.")

    try:
        while True:
            current = fetch_data(endpoint_url)
            new_signals = [sig for sig in current if sig not in history]

            for sig in new_signals:
                achieved1 = sig.get('Achieved1', False)
                achieved2 = sig.get('Achieved2', False)
                # if it's a new signal, format and send it if it's exit make it reply
                if not (achieved1 or achieved2):
                    

                    msg = format_signal(sig)

                    message_sent = client.send_message(channel_peer_id, msg)
                    symbol_ids_msg[sig.get('Pair', '').upper()] = message_sent.id
                    print(f"Sent: {msg}")
                else:
                    symbol = sig.get('Pair', '').upper()
                    if symbol in symbol_ids_msg:
                        msg_id = symbol_ids_msg[symbol]
                        reply_msg = format_signal(sig)
                        client.send_message(channel_peer_id, reply_msg, reply_to=msg_id)
                        print(f"Replied to message ID {msg_id} for {symbol}")

            history = current.copy()
            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print("Stopping signal bot...")
    finally:
        client.disconnect()


if __name__ == '__main__':
    main()
