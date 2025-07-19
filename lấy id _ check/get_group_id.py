from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import os

api_id = 22044709  # ← thay bằng api_id của anh
api_hash = '3589210c1c700fb2b44f5427e4305819'  # ← thay bằng api_hash của anh
phone = '+84856819217'  # ← thay bằng số điện thoại Telegram của anh

client = TelegramClient('session_name', api_id, api_hash)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input('Nhập mã OTP từ Telegram: '))

# Lấy danh sách các cuộc trò chuyện (group/channel/PM)
chats = []
last_date = None
chunk_size = 200

result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=chunk_size,
    hash=0
))
chats.extend(result.chats)

# In ra danh sách để tìm group
print("\n===== DANH SÁCH GROUP/CHANNEL =====\n")
for i, chat in enumerate(chats):
    try:
        print(f"{i}. {chat.title} — ID: {chat.id}")
    except:
        continue