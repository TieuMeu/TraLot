# mt5_trading.py
ORDER_BUY_LIMIT     = 2
ORDER_SELL_LIMIT    = 3
ORDER_BUY_STOP      = 4
ORDER_SELL_STOP     = 5
import MetaTrader5 as mt5
from config import lot_size, slippage, magic_number

# === Kết nối MT5 ===
def connect_mt5():
    if not mt5.initialize():
        raise Exception("Lỗi kết nối MetaTrader5: " + str(mt5.last_error()))
    print("✅ Kết nối MT5 thành công~!")

# === Đặt lệnh Buy hoặc Sell ===
def send_order(symbol, order_type, volume, entry, sl=None, tp=None):
    if not mt5.initialize():
        print("❌ Không kết nối được MT5~")
        return False

    print("✅ Kết nối MT5 thành công~!")

    # Lấy giá hiện tại
    price_info = mt5.symbol_info_tick(symbol)
    if order_type == 'buy':
        current_price = price_info.ask
    else:
        current_price = price_info.bid

    # Xác định loại lệnh chờ phù hợp
    if order_type == 'buy':
        order_type_mt5 = (
            ORDER_BUY_STOP if entry > current_price
            else ORDER_BUY_LIMIT
        )
    else:
        order_type_mt5 = (
            ORDER_SELL_STOP if entry < current_price
            else ORDER_SELL_LIMIT
        )

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

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Gửi lệnh thất bại: {result.retcode} — {result.comment}")
        return False
    print("✅ Đặt lệnh chờ thành công~!!")
    return True

# === Ngắt kết nối khi xong ===
def disconnect_mt5():
    mt5.shutdown()