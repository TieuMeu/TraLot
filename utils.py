# utils.py
import MetaTrader5 as mt5
import re
from config import symbol_map, entry_price_index, ORDER_SPLIT
from telegram import Bot

TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN_HERE'  # ← nhớ sửa bằng token thật
bot = Bot(token=TELEGRAM_TOKEN)


def extract_order_data(text):
    lines = text.lower().splitlines()

    order_type = None
    symbol = None
    entry = None
    sl = None
    tp_list = []
    comment = None

    for line in lines:
        if 'buy' in line:
            order_type = 'buy'
        elif 'sell' in line:
            order_type = 'sell'

        for key in symbol_map:
            if key in line:
                symbol = symbol_map[key]
                break

        if re.search(r'\d{3,5}-\d{3,5}', line):
            entry_range = re.findall(r'\d{3,5}', line)
            if entry_range:
                entry = float(entry_range[entry_price_index])

        if 'sl' in line:
            sl_match = re.findall(r'\d{3,5}', line)
            if sl_match:
                sl = float(sl_match[0])

        if 'tp' in line or 'take' in line:
            if 'pip' in line:
                pip_match = re.findall(r'(\d+)\s*pip', line)
                if pip_match:
                    pip_value = int(pip_match[0])
                    step = pip_value / ORDER_SPLIT
                    for i in range(1, ORDER_SPLIT + 1):
                        if order_type == 'buy':
                            tp_price = entry + step * i / 10  # 50 pip = 5.0
                        else:
                            tp_price = entry - step * i / 10
                        tp_list.append(round(tp_price, 2))
            else:
                tp_values = re.findall(r'\d{3,5}', line)
                for val in tp_values:
                    tp_list.append(float(val))

    if not all([order_type, symbol, entry, sl]) or len(tp_list) != ORDER_SPLIT:
        raise ValueError("Thông tin tín hiệu chưa đầy đủ hoặc số TP không khớp!")

    return {
        'type': order_type,
        'symbol': symbol,
        'entry': entry,
        'sl': sl,
        'tp': tp_list,
        'comment': comment
    }

def send_telegram_message(text):
    bot.send_message(chat_id='YOUR_CHAT_ID_HERE', text=text)
    
def get_orders_by_comment(symbol, comment):
    orders = mt5.positions_get(symbol=symbol)
    filtered_orders = []
    if orders:
        for order in orders:
            if comment in order.comment:
                filtered_orders.append(order)
    return filtered_orders