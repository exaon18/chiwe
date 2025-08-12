from telethon.sync import TelegramClient
from telethon.errors import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
import csv
import time

# === Your Telegram credentials ===
api_id = 21591381
api_hash = 'cef653192457e9af612c1eea71f14332'
phone = '+251983312530'

# === Start the Telegram client ===
client = TelegramClient('adder', api_id, api_hash)
client.start(phone)

# === Target group (your group, where you want to add people) ===
target_group = client.get_entity('zioniksi')  # Replace with your group username

# === Load users from CSV (only those with a username) ===
users = []
with open('members.csv', encoding='utf-8') as f:
    rows = csv.reader(f)
    next(rows)  # skip header
    for row in rows:
        user = {}
        user['username'] = row[0]
        user['id'] = row[1]  # keep as string just for reference
        if user['username']:  # only include if username exists
            users.append(user)

print(f"✅ Loaded {len(users)} users with usernames")

# === Add users one by one ===
n = 0
for user in users:
    n += 1
    try:
        user_entity = client.get_input_entity(user['username'])
        print(f"➕ Adding {user['username']}...")
        client(InviteToChannelRequest(target_group, [user_entity]))
        print(f"✅ {user['username']} added.")

        # Sleep to avoid flood
        time.sleep(10)

        if n % 20 == 0:
            print("⏸️ Resting for 60s after 20 adds...")
            time.sleep(60)

    except PeerFloodError:
        print("🚫 PeerFloodError: Telegram thinks you're spamming. Resting 10 minutes.")
        time.sleep(600)
    except UserPrivacyRestrictedError:
        print(f"🚷 Skipped {user['username']} — privacy settings block adds.")
    except Exception as e:
        print(f"❌ Failed to add {user['username']}: {e}")

print("🎯 Done adding users.")
