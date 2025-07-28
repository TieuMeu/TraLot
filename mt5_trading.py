# mt5_trading.py
import MetaTrader5 as mt5
ORDER_BUY_LIMIT     = 2
ORDER_SELL_LIMIT    = 3
ORDER_BUY_STOP      = 4
ORDER_SELL_STOP     = 5

from config import lot_size, slippage, magic_number
from config import symbol_map
# === Kết nối MT5 ===
def connect_mt5():
    if not mt5.initialize():
        raise Exception("Lỗi kết nối MetaTrader5: " + str(mt5.last_error()))
    print("✅ Kết nối MT5 thành công~!")

def get_current_price(symbol):
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        raise Exception(f"Cannot get price for {symbol}")
    return tick.ask, tick.bid

def get_orders_by_comment(comment):
    positions = mt5.positions_get()
    if positions is None:
        return []
    return [p for p in positions if comment in p.comment]

def close_order(ticket, lot, price, deviation=20):
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": ticket,
        "volume": lot,
        "price": price,
        "deviation": deviation,
        "type": mt5.ORDER_TYPE_SELL if price > 0 else mt5.ORDER_TYPE_BUY,
        "magic": 234000,
        "comment": "auto close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    return mt5.order_send(request)

# Sửa chỗ này nhen!
def modify_order(ticket, new_sl=None, new_tp=None):
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": ticket,
        "sl": new_sl,
        "tp": new_tp,
        "magic": 234000,
        "comment": "modify order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Failed to modify order #{ticket}: {result.retcode}")
    else:
        print(f"✅ Order #{ticket} modified: SL={new_sl}, TP={new_tp}")
# === Đặt lệnh Buy hoặc Sell ===
def send_order(symbol, order_type, volume, entry, sl, tp):
    if not mt5.initialize():
        print("❌ Không kết nối được MT5~")
        return False

    print("✅ Kết nối MT5 thành công~!")

    # Chuyển tên symbol nếu cần
    symbol = symbol_map.get(symbol.lower(), symbol)

    # Lấy giá thị trường hiện tại
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        print("❌ Không lấy được giá thị trường~")
        return False

    market_price = tick.ask if order_type.lower() == "buy" else tick.bid

    # Xác định loại lệnh chờ phù hợp (limit hay stop)
    if order_type.lower() == "buy":
        order_type_mt5 = mt5.ORDER_TYPE_BUY_STOP if entry > market_price else mt5.ORDER_TYPE_BUY_LIMIT
    else:
        order_type_mt5 = mt5.ORDER_TYPE_SELL_STOP if entry < market_price else mt5.ORDER_TYPE_SELL_LIMIT

    # Cấu hình lệnh
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": order_type_mt5,
        "price": entry,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": "AutoTrade by GPT Loli~",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    print("⚙️ Lệnh chờ sắp đặt:", request)

    # Gửi lệnh
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Gửi lệnh thất bại: {result.retcode} — {result.comment} — {result}")
        return False

    print("✅ Đặt lệnh chờ thành công~!!")
    return True

# === Ngắt kết nối khi xong ===
def disconnect_mt5():
    mt5.shutdown()