# price_watcher.py
import MetaTrader5 as mt5
import threading
import time
from config import PRICE_CHECK_INTERVAL, TP_LEVELS, TP_TRAILING
from mt5_trading import get_current_price, modify_order, close_order, get_orders_by_comment
from utils import send_telegram_message
from utils import get_orders_by_comment
entry_global = None
symbol_global = None
order_type_global = None
tp_hits = [False, False, False]

def start_price_watcher(symbol, entry, order_type):
    global symbol_global, entry_global, order_type_global, tp_hits
    symbol_global = symbol
    entry_global = entry
    order_type_global = order_type
    tp_hits = [False, False, False]

    thread = threading.Thread(target=watch_price_loop)
    thread.daemon = True
    thread.start()
def get_current_price(symbol, order_type):
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None
    return tick.ask if order_type == "buy" else tick.bid
def watch_price_loop():
    while not all(tp_hits):
        time.sleep(PRICE_CHECK_INTERVAL)
        current = get_current_price(symbol_global, order_type_global)

        for i in range(3):
            tp_price = calculate_tp_price(entry_global, TP_LEVELS[i], order_type_global)
            orders = get_orders_by_comment(symbol_global, f"TP{i+1}")
            for order in orders:
                if should_close(current, tp_price, order_type_global) and not tp_hits[i]:
                    close_order(order)
                    tp_hits[i] = True
                    send_telegram_message(f"🎯 *TP{i+1} HIT:* Lệnh `{order.comment}` đã chạm TP và được đóng.")

        update_sl_after_tp()

def calculate_tp_price(entry, pip, order_type):
    if order_type == "buy":
        return entry + pip * 0.01
    else:
        return entry - pip * 0.01

def should_close(current, target, order_type):
    return current >= target if order_type == "buy" else current <= target

def update_sl_after_tp():
    if tp_hits[0] and not tp_hits[1]:
        # Dời SL TP2+3 về Entry +10 pip
        new_sl = calculate_tp_price(entry_global, 10, order_type_global)
        for i in [1, 2]:
            orders = get_orders_by_comment(symbol_global, f"TP{i+1}")
            for order in orders:
                modify_order(order, new_sl=new_sl)
                send_telegram_message(f"🔁 *DỜI SL:* SL của lệnh `{order.comment}` đã được dời về `{new_sl}`.")

    if tp_hits[1] and not tp_hits[2]:
        # Dời SL TP3 về TP1
        sl = calculate_tp_price(entry_global, TP_LEVELS[0], order_type_global)
        orders = get_orders_by_comment(symbol_global, "TP3")
        for order in orders:
            modify_order(order, new_sl=sl)
            send_telegram_message(f"🔁 *DỜI SL:* SL của lệnh `{order.comment}` đã được dời về `{new_sl}`.")

    if tp_hits[2] and TP_TRAILING:
        # Dời SL TP3 về TP2
        sl = calculate_tp_price(entry_global, TP_LEVELS[1], order_type_global)
        orders = get_orders_by_comment(symbol_global, "TP3")
        for order in orders:
            modify_order(order, new_sl=sl)
            send_telegram_message(f"🔁 *DỜI SL:* SL của lệnh `{order.comment}` đã được dời về `{new_sl}`.")

def handle_message_update(text):
    lower = text.lower()
    if "dời sl" in lower or "chốt" in lower:
        sl = calculate_tp_price(entry_global, 10, order_type_global)
        for i in [1, 2]:
            orders = get_orders_by_comment(symbol_global, f"TP{i+1}")
            for order in orders:
                modify_order(order, new_sl=sl)
                send_telegram_message(f"🔁 *DỜI SL (theo yêu cầu):* SL của lệnh `{order.comment}` đã được dời về `{sl}`.")
    
