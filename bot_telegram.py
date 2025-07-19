# bot_telegram.py
import MetaTrader5 as mt5
import asyncio
from telethon import TelegramClient, events
from config import api_id, api_hash, phone_number, group_id
from utils import extract_order_data
from mt5_trading import send_order
import os
import re
from datetime import datetime
# from order_tracker import move_sl_to_breakeven, close_positions_if_profit
from order_manager import send_split_orders
from price_watcher import start_price_watcher, handle_message_update
# === Ghi log đơn giản ===
def write_log(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists("logs"):
        os.makedirs("logs")
    with open("logs/bot_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {message}\n")

# === Tạo client Telethon ===
client = TelegramClient('bot_session', api_id, api_hash)

async def main():
    await client.start(phone=phone_number)
    print("🐾 Bot Telegram đã sẵn sàng đọc tín hiệu~!!")

    @client.on(events.NewMessage(chats=group_id))
    async def handle_message(event):
        text = event.message.message
        print(f"\n📥 Nhận tin nhắn:\n{text}")
        write_log(f"Nhận tín hiệu:\n{text}")

        # Xử lý yêu cầu "dời sl", "chốt"
        # if any(key in text.lower() for key in ["dời sl", "chốt"]):
        #     moved = move_sl_to_breakeven("XAUUSD")
        #     if moved:
        #         print(f"✅ Đã dời SL cho các lệnh: {moved}")
        if any(key in text.lower() for key in ["dời sl", "chốt", "pip"]):
             handle_message_update(text)
        # Xử lý yêu cầu +N pip
        pip_match = re.search(r'\+(\d+)\s*pip', text.lower())
        if pip_match:
            pip_target = int(pip_match.group(1))
            closed = close_positions_if_profit("XAUUSD", pip_target)
            if closed:
                print(f"✅ Đã chốt lời các lệnh: {closed}")
        
        # Phân tích lệnh giao dịch mới
        order = extract_order_data(text)
        if order:
            try:
                send_split_orders(
                 symbol=order["symbol"],
                 order_type=order["type"],
                 entry=order["entry"],
                 sl_pip=order["sl"],
                 tp_levels=order["tp"]
                )
                start_price_watcher(order["symbol"], order["entry"], order["type"])
                msg = f"✅ Gửi lệnh {order['type'].upper()} {order['symbol']} thành công!"
                print(msg)
                write_log(msg)
            except Exception as e:
                err = f"❌ Gửi lệnh thất bại: {e}"
                print(err)
                write_log(err)
        else:
            print("⚠️ Không nhận dạng được lệnh trong tin nhắn này.")
            write_log("Không hiểu tín hiệu, bỏ qua.")

    await client.run_until_disconnected()
        
# === Chạy bot ===
if __name__ == "__main__":
    asyncio.run(main())