# config.py

# === Telegram API Credentials ===
api_id = 22044709  # ← thay bằng api_id của anh
api_hash = '3589210c1c700fb2b44f5427e4305819'  # ← thay bằng api_hash của anh
phone_number = '+84856819217'  # ← thay bằng số điện thoại Telegram của anh

# === Group Telegram cần đọc ===
group_id = 4897086094  # ID group test cá nhân

# === MetaTrader5 Config ===
symbol_map = {
    'vàng': 'XAUUSD',
    'gold': 'XAUUSD',
    'xau': 'XAUUSD'
}

# === Trading Settings ===
lot_size = 0.02  # Khối lượng mặc định cho mỗi lệnh
entry_price_index = 0  # 0: lấy giá đầu tiên trong chuỗi như 3333-3321
slippage = 10  # Slippage (giá trượt)
magic_number = 123456  # Mã định danh lệnh (để phân biệt bot)

ORDER_SPLIT = 3  # Chia lệnh thành 3 phần
TP_LEVELS = [30, 50, 80]  # Mỗi TP tương ứng số pip
TP_TRAILING = True  # Bật chế độ trailing nếu TP3 chưa bị hit
PRICE_CHECK_INTERVAL = 1  # Kiểm tra giá mỗi 1 giây
SL_PIP = 30  # Stop loss mặc định (pip)
SYMBOL = "XAUUSD"  # Mặc định cặp giao dịch
VOLUME = 0.02  # Volume tổng

TELEGRAM_BOT_TOKEN = "6xxxxxxxxx:AAxxxxxxxxxxxx"  # thay token thật vào đây
TELEGRAM_CHAT_ID = "4897086094"  # ID nhóm hoặc ID cá nhân Telegram