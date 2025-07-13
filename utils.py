# utils.py

import re
from config import symbol_map, entry_price_index

def extract_order_data(text):
    lines = text.lower().splitlines()
    
    order_type = None
    symbol = None
    entry_price = None
    stop_loss = None
    take_profit = None

    for line in lines:
        # 1. Loại lệnh
        if 'buy' in line:
            order_type = 'buy'
        elif 'sell' in line:
            order_type = 'sell'

        # 2. Symbol & Entry
        for key in symbol_map:
            if key in line:
                symbol = symbol_map[key]
                # Tìm các giá trong dạng: 3333-3321
                price_match = re.findall(r'\d{3,5}', line)
                if price_match and len(price_match) >= 1:
                    entry_price = float(price_match[entry_price_index])
                break

        # 3. SL
        if 'sl' in line:
            sl_match = re.search(r'\d{3,5}', line)
            if sl_match:
                stop_loss = float(sl_match.group())

        # 4. TP
        if 'tp' in line:
            pip_match = re.search(r'(\d+)\s*pip', line)  # <- chuyển ra ngoài trước
            if pip_match and entry_price:
                pip_val = int(pip_match.group(1))
                pip_value = 0.1  # vàng = 0.1 USD/pip
                take_profit = (
                    entry_price + pip_val * pip_value
                    if order_type == 'buy'
                    else entry_price - pip_val * pip_value
        )
    else:
        tp_match = re.search(r'\d{3,5}', line)
        if tp_match:
            take_profit = float(tp_match.group())

    # Trả về kết quả nếu đủ dữ liệu
    if all([order_type, symbol, entry_price]):
        return {
            'type': order_type,
            'symbol': symbol,
            'entry': entry_price,
            'sl': stop_loss,
            'tp': take_profit
        }
    else:
        return None