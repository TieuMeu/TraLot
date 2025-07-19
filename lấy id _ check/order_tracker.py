import MetaTrader5 as mt5

def get_open_orders(symbol):
    orders = mt5.positions_get(symbol=symbol)
    if orders is None:
        return []
    return list(orders)

def move_sl_to_breakeven(symbol, buffer_pip=10):
    positions = get_open_orders(symbol)
    point = mt5.symbol_info(symbol).point
    moved = []

    for pos in positions:
        entry = pos.price_open
        if pos.type == 0:  # Buy
            new_sl = entry + buffer_pip * point
        else:  # Sell
            new_sl = entry - buffer_pip * point

        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": pos.ticket,
            "sl": new_sl,
            "tp": pos.tp,
        }

        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            moved.append(pos.ticket)

    return moved

def close_positions_if_profit(symbol, target_pip):
    positions = get_open_orders(symbol)
    point = mt5.symbol_info(symbol).point
    closed = []

    for pos in positions:
        current_price = mt5.symbol_info_tick(symbol).bid if pos.type == 1 else mt5.symbol_info_tick(symbol).ask
        profit_pips = abs(current_price - pos.price_open) / point

        if profit_pips >= target_pip:
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": pos.ticket,
                "symbol": symbol,
                "volume": pos.volume,
                "type": mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY,
                "price": current_price,
                "deviation": 10,
                "magic": 123456,
                "comment": f"Chốt lời +{target_pip}pip",
            }
            result = mt5.order_send(close_request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                closed.append(pos.ticket)

    return closed