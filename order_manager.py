# order_manager.py

from config import SYMBOL, VOLUME, ORDER_SPLIT, TP_LEVELS, SL_PIP
import MetaTrader5 as mt5

# Hàm gửi 1 lệnh
def send_order(action=1, symbol=SYMBOL, volume=0.01, order_type=0, price=0.0, sl=0.0, tp=0.0, deviation=10):
    request = {
        "action": action,            # 1: market, 5: pending
        "symbol": symbol,
        "volume": volume,
        "type": order_type,          # 0: buy, 1: sell, 2: buy limit, 3: sell limit, 4: buy stop, 5: sell stop
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 123456,
        "comment": "AutoTrade by GPT Loli~",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    result = mt5.order_send(request)

    if result is None:
        print("❌ Lỗi: Không có phản hồi từ MT5~")
        return False

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Gửi lệnh thất bại: {result.retcode} — {result.comment} — {result}")
        return False

    print(f"✅ Lệnh được gửi thành công! ID: {result.order}")
    return True

# Hàm tạo & gửi các lệnh chia theo TP
def send_split_orders(entry_price, direction="sell"):
    orders = []
    volume_per_order = round(VOLUME / ORDER_SPLIT, 2)

    sl_price = 0
    if direction == "buy":
        sl_price = round(entry_price - SL_PIP * 0.01, 3)
    elif direction == "sell":
        sl_price = round(entry_price + SL_PIP * 0.01, 3)
    else:
        print("❌ Hướng lệnh không hợp lệ~")
        return

    for i in range(ORDER_SPLIT):
        tp_pip = TP_LEVELS[i]
        if direction == "buy":
            tp_price = round(entry_price + tp_pip * 0.01, 3)
            order_type = mt5.ORDER_TYPE_BUY_LIMIT if entry_price < mt5.symbol_info_tick(SYMBOL).ask else mt5.ORDER_TYPE_BUY_STOP
        else:
            tp_price = round(entry_price - tp_pip * 0.01, 3)
            order_type = mt5.ORDER_TYPE_SELL_LIMIT if entry_price > mt5.symbol_info_tick(SYMBOL).bid else mt5.ORDER_TYPE_SELL_STOP

        success = send_order(
            action=mt5.TRADE_ACTION_PENDING,
            symbol=SYMBOL,
            volume=volume_per_order,
            order_type=order_type,
            price=entry_price,
            sl=sl_price,
            tp=tp_price
        )

        if not success:
            print(f"❌ Gửi lệnh thứ {i+1} thất bại~")
        else:
            print(f"✅ Lệnh thứ {i+1} đã gửi với TP: {tp_price}, SL: {sl_price}")