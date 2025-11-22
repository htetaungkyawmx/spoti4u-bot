import logging
import re
import sqlite3
import threading
from datetime import datetime
import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "8540709881:AAHGbtI_OzPC_LOo84VEz4Oo-2f_hZPrRQs"
FOUNDER_ID = 5048500757
SHOP_NAME = "Spoti4U Premium Digital Services"
ADMIN_USERNAME = "@saisainghtet"
ADMIN_PHONE = "09445265001"

bot = telebot.TeleBot(BOT_TOKEN)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class ConversationDB:
    def __init__(self):
        self.conn = sqlite3.connect('conversations.db', check_same_thread=False)
        self.create_tables()
        self.lock = threading.Lock()
    
    def create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_name TEXT,
                    message_text TEXT,
                    message_type TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    replied BOOLEAN DEFAULT FALSE,
                    reply_text TEXT
                )
            ''')
    
    def save_message(self, user_id, user_name, message_text, message_type="customer"):
        with self.lock:
            self.conn.execute('''
                INSERT INTO conversations (user_id, user_name, message_text, message_type)
                VALUES (?, ?, ?, ?)
            ''', (user_id, user_name, message_text, message_type))
            self.conn.commit()
    
    def get_pending_messages(self):
        with self.lock:
            cursor = self.conn.execute('''
                SELECT * FROM conversations 
                WHERE replied = FALSE AND message_type = 'customer'
                ORDER BY timestamp DESC
            ''')
            return cursor.fetchall()
    
    def mark_as_replied(self, message_id, reply_text):
        with self.lock:
            self.conn.execute('''
                UPDATE conversations 
                SET replied = TRUE, reply_text = ?
                WHERE id = ?
            ''', (reply_text, message_id))
            self.conn.commit()
    
    def get_user_conversation(self, user_id, limit=10):
        with self.lock:
            cursor = self.conn.execute('''
                SELECT * FROM conversations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
            return cursor.fetchall()

db = ConversationDB()

AUTO_REPLIES = {
    r'(vpn|ဗွီပီအန်|vpn service|vpn key)': 
        "🔒 VPN Services - Premium VPN Keys\n\n"
        "⚡ High Speed Connection\n"
        "🌍 Multiple Server Locations\n"
        "🛡️ 30 Days Warranty\n"
        "🚀 Instant Delivery\n\n"
        "📍 Available Servers:\n"
        "• 🇧🇷 Brazil Server\n"
        "• 🇵🇭 Philippines Server\n"
        "• 🇸🇬 Singapore Server\n"
        "• 🇺🇸 USA Server\n\n"
        "💵 စျေးနှုန်းအတွက် Spoti4U App ထဲတွင်ကြည့်ရှုနိုင်ပါသည်။ 📱",

    r'(game account|ဂိမ်းအကောင့်|ml|pubg|mobile legends|magic chess|ဂိမ်း)': 
        "🎮 Game Accounts\n\n"
        "🎯 Available Games:\n"
        "• 📱 Mobile Legends Accounts\n"
        "• 🎯 PUBG Mobile Accounts\n"
        "• ♟️ Magic Chess Accounts\n"
        "• 🏆 Various Ranks Available\n\n"
        "📊 Available Ranks:\n"
        "• ⚔️ Warrior to Mythic (ML)\n"
        "• 🎖️ Bronze to Conqueror (PUBG)\n"
        "• 📈 Low to High Rank (Magic Chess)\n\n"
        "🛡️ 7 Days Warranty\n\n"
        "💵 စျေးနှုန်းအတွက် Spoti4U App ထဲတွင်ကြည့်ရှုနိုင်ပါသည်။ 📱",

    r'(premium app|ပရီမီယံအက်ပ်|spotify|netflix|youtube|zoom|အက်ပ်)': 
        "📱 Premium Apps\n\n"
        "🎵 Spotify Premium\n"
        "🎬 Netflix Premium\n"
        "📺 YouTube Premium\n"
        "💼 Zoom Premium\n"
        "🐭 Disney+ Accounts\n"
        "🍎 Apple Music\n\n"
        "✨ Features:\n"
        "• 🚫 No Advertisement\n"
        "• 🎥 Full HD/4K Quality\n"
        "• 📱 Multiple Devices\n"
        "• 🔄 Auto-renewal\n\n"
        "💵 စျေးနှုန်းအတွက် Spoti4U App ထဲတွင်ကြည့်ရှုနိုင်ပါသည်။ 📱",

    r'(gift card|လက်ဆောင်ကတ်|google play|itunes|steam|wallet code|ဂစ်ကတ်)': 
        "🎁 Gift Cards & Wallet Codes\n\n"
        "🛒 Available Cards:\n"
        "• 📱 Google Play Gift Cards\n"
        "• 🎵 iTunes Gift Cards\n"
        "• 🎮 Steam Wallet Codes\n"
        "• 💰 Razer Gold PINs\n"
        "• 💵 Various Denominations\n\n"
        "💰 Available Denominations:\n"
        "• $10, $25, $50, $100\n"
        "• 🌍 Region Specific Cards\n"
        "• ⚡ Instant Delivery\n\n"
        "💵 စျေးနှုန်းအတွက် Spoti4U App ထဲတွင်ကြည့်ရှုနိုင်ပါသည်။ 📱",

    r'(ဘယ်လိုဝယ်ရမလဲ|ဝယ်ယူနည်း|ဘယ်လိုဝယ်မလဲ|how to buy|purchase|အသုံးပြုနည်း)': 
        "🛒 ဝယ်ယူနည်း အဆင့်ဆင့်\n\n"
        "1️⃣ Spoti4U App ကိုဖွင့်ပါ\n"
        "   📱 Service ရွေးချယ်ပါ\n"
        "   👀 Product ကြည့်ရှုပါ\n\n"
        "2️⃣ ငွေဖြည့်သွင်းပါ\n"
        "   💰 Wallet Top-up လုပ်ပါ\n"
        "   🏦 KBZ Pay / Wave Pay\n\n"
        "3️⃣ Product ဝယ်ယူပါ\n"
        "   🛍️ Add to Cart\n"
        "   ✅ Checkout\n\n"
        "4️⃣ Product ရယူပါ\n"
        "   ⚡ Instant Delivery\n"
        "   📋 Purchase History\n\n"
        "💵 စျေးနှုန်းများကို App ထဲတွင်ကြည့်ရှုနိုင်ပါသည်။ 📱",

    r'(စျေးနှုန်း|ဈေးနှုန်း|ဘယ်လောက်လဲ|price|cost|ဈေး)': 
        "💰 စျေးနှုန်းများ\n\n"
        "📱 စျေးနှုန်းများကို Spoti4U App ထဲတွင်သာ ကြည့်ရှုနိုင်ပါသည်။\n\n"
        "✨ App ထဲမှာ ရရှိနိုင်သော အချက်အလက်များ:\n"
        "• ⏱️ Real-time စျေးနှုန်းများ\n"
        "• 🔄 အချိန်နှင့်တစ်ပြေးညီ Update\n"
        "• 🎉 Promotion နှင့် Discount များ\n"
        "• 📦 Product Availability\n\n"
        "📲 Spoti4U App ကို ဒေါင်းလုဒ်ရယူပြီး စျေးနှုန်းများကိုကြည့်ရှုပါ။",

    r'(အာမခံ|warranty|ပြန်လည်သွင်း|replace|အာမခံချက်)': 
        "🛡️ အာမခံစနစ်\n\n"
        "📅 Warranty Period:\n"
        "• 📦 Digital Products - 30 ရက်အာမခံ\n"
        "• 🔒 VPN Services - 30 ရက်အာမခံ\n"
        "• 🎮 Game Accounts - 7 ရက်အာမခံ\n"
        "• 🎁 Gift Cards - No Warranty (Instant Delivery)\n\n"
        "🔧 Support:\n"
        "• ⏰ 24 နာရီအတွင်း အခမဲ့ပြန်လည်သွင်းပေးခြင်း\n"
        "• 📞 24/7 Customer Support\n"
        "• 🛠️ Technical Assistance",

    r'(ငွေလွှဲနည်း|payment|pay|KBZ|Wave|ပေးချေမှု)': 
        "💳 ငွေပေးချေမှုနည်းလမ်းများ\n\n"
        "📱 Spoti4U App ထဲမှ ငွေဖြည့်သွင်းနည်း:\n"
        "1. App ထဲတွင် '💰 Wallet' ကိုနှိပ်ပါ\n"
        "2. '💵 Top-up' ကိုရွေးချယ်ပါ\n"
        "3. ဖြည့်သွင်းလိုသောပမာဏထည့်ပါ\n"
        "4. 🏦 KBZ Pay သို့မဟုတ် Wave Pay ဖြင့်ငွေလွှဲပါ\n\n"
        "✅ Supported Payment Methods:\n"
        "• 🟣 KBZ Pay\n"
        "• 🟢 Wave Pay\n\n"
        "💡မှတ်ချက်: ငွေဖြည့်သွင်းပြီးပါက ချက်ချင်း Wallet Balance တိုးသွားမည်။",

    r'(app|application|အက်ပ်ဒေါင်းလုဒ်|download|အက်ပ်)': 
        "📱 Spoti4U Application\n\n"
        "🎯 App ထဲတွင် ရရှိနိုင်သော ဝန်ဆောင်မှုများ:\n"
        "• 🔒 VPN Services\n"
        "• 🎮 Game Accounts\n"
        "• 📱 Premium Apps\n"
        "• 🎁 Gift Cards\n"
        "• 💰 Wallet System\n"
        "• 📋 Purchase History\n\n"
        "✨ Features:\n"
        "• ⏱️ Real-time Pricing\n"
        "• ⚡ Instant Delivery\n"
        "• 💳 Easy Payment\n"
        "• 📞 24/7 Support\n"
        "• 🛡️ Warranty System\n\n"
        "📲 App ကိုဒေါင်းလုဒ်ရယူပြီး ဝန်ဆောင်မှုများကို အပြည့်အဝခံစားပါ။",

    r'(လက်ကျန်|balance|ပိုက်ဆံအိတ်|wallet|ဘတ်ဂျက်)': 
        "💰 Wallet System\n\n"
        "📱 Spoti4U App ထဲတွင် Wallet System ပါရှိပါသည်:\n\n"
        "✨ Features:\n"
        "• 💵 ငွေဖြည့်သွင်းနိုင်ခြင်း\n"
        "• 👀 လက်ကျန်ကြည့်ရှုနိုင်ခြင်း\n"
        "• 🛒 အလွယ်တကူဝယ်ယူနိုင်ခြင်း\n"
        "• 📊 Transaction History ကြည့်ရှုနိုင်ခြင်း\n"
        "• 📈 Spending Tracking\n\n"
        "🏦 Payment Methods:\n"
        "• 🟣 KBZ Pay\n"
        "• 🟢 Wave Pay\n\n"
        "💡 ငွေဖြည့်သွင်းရန် App ထဲမှာ Wallet Section သို့သွားပါ။",

    r'(server|ဆာဗာ|brazil|philippines|singapore|usa|location)': 
        "🌐 Server Information\n\n"
        "📍 Available Server Locations:\n"
        "• 🇧🇷 Brazil Server\n"
        "• 🇵🇭 Philippines Server\n"
        "• 🇸🇬 Singapore Server\n"
        "• 🇺🇸 USA Server\n"
        "• 🇪🇺 Europe Server\n"
        "• 🇯🇵 Japan Server\n\n"
        "⚡ Server Features:\n"
        "• 🚀 High Speed Connection\n"
        "• 📍 Low Latency\n"
        "• 🔒 Stable Connection\n"
        "• 🌍 Multiple Locations\n\n"
        "🔒 VPN Services အတွက် Server များစွာရှိပါသည်။",

    r'(ဆက်သွယ်ရန်|contact|support|အကူအညီ|help|ကူညီ)': 
        "📞 ဆက်သွယ်ရန်\n\n"
        "👨‍💼 Admin နှင့်ဆက်သွယ်ရန်:\n"
        "• 👤 Username: " + ADMIN_USERNAME + "\n"
        "• 📱 Phone: " + ADMIN_PHONE + "\n\n"
        "⏰ Working Hours:\n"
        "• 24/7 Customer Support\n"
        "• ⚡ Instant Response\n\n"
        "🔧 Quick Support:\n"
        "• 🛠️ Technical Issues\n"
        "• 💰 Payment Problems\n"
        "• 📦 Product Delivery\n\n"
        "💬 မြန်ဆန်သော အကူအညီရရှိရန် Admin ကိုတိုက်ရိုက်ဆက်သွယ်ပါ။",

    r'(မင်္ဂလာပါ|hello|hi|နေကောင်းလား|hey|halo)': 
        f"👋 မင်္ဂလာပါ! {SHOP_NAME} မှ ကြိုဆိုပါတယ်! 🎉\n\n"
        "✨ ကျေးဇူးပြု၍ အောက်ပါ option များမှ ရွေးချယ်နိုင်ပါသည်:\n\n"
        "• 🔒 VPN Services\n"
        "• 🎮 Game Accounts\n"
        "• 📱 Premium Apps\n"
        "• 🎁 Gift Cards\n"
        "• 🛒 How to Buy\n"
        "• 📞 Contact Support\n\n"
        "💬 သို့မဟုတ် သင့်မေးခွန်းကိုတိုက်ရိုက်ရိုက်ထည့်မေးမြန်းနိုင်ပါသည်။",

    r'(ဝန်ဆောင်မှု|services|ဘာတွေရလဲ|products|ဝန်ဆောင်မှုများ)': 
        "🛍️ ရရှိနိုင်သော ဝန်ဆောင်မှုများ\n\n"
        "🔒 VPN Services\n"
        "• Premium VPN Keys\n"
        "• Multiple Servers\n\n"
        "🎮 Game Accounts\n"
        "• Mobile Legends\n"
        "• PUBG Mobile\n"
        "• Magic Chess\n\n"
        "📱 Premium Apps\n"
        "• Spotify, Netflix, YouTube\n"
        "• Zoom, Disney+, Apple Music\n\n"
        "🎁 Gift Cards\n"
        "• Google Play, iTunes\n"
        "• Steam, Razer Gold\n\n"
        "💵 စျေးနှုန်းများကို Spoti4U App ထဲတွင်ကြည့်ရှုနိုင်ပါသည်။ 📱"
}

def create_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton("🔒 VPN Services"),
        KeyboardButton("🎮 Game Accounts"),
        KeyboardButton("📱 Premium Apps"),
        KeyboardButton("🎁 Gift Cards"),
        KeyboardButton("🛒 How to Buy"),
        KeyboardButton("💰 Prices"),
        KeyboardButton("🛡️ Warranty"),
        KeyboardButton("📞 Contact"),
        KeyboardButton("📲 Download App")
    ]
    keyboard.add(*buttons)
    return keyboard

def create_admin_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton("📨 Pending Messages"),
        KeyboardButton("📊 Statistics"),
        KeyboardButton("🔍 Search User"),
        KeyboardButton("📢 Broadcast"),
        KeyboardButton("🔄 Refresh"),
        KeyboardButton("❌ Close Admin")
    ]
    keyboard.add(*buttons)
    return keyboard

def create_inline_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("🔒 VPN Services", callback_data="vpn_services"),
        InlineKeyboardButton("🎮 Game Accounts", callback_data="game_accounts"),
        InlineKeyboardButton("📱 Premium Apps", callback_data="premium_apps"),
        InlineKeyboardButton("🎁 Gift Cards", callback_data="gift_cards"),
        InlineKeyboardButton("🛒 How to Buy", callback_data="how_to_buy"),
        InlineKeyboardButton("💰 Check Prices", callback_data="check_prices"),
        InlineKeyboardButton("🛡️ Warranty Info", callback_data="warranty_info"),
        InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")
    ]
    keyboard.add(*buttons)
    return keyboard

def create_reply_keyboard(user_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("💬 Reply to User", callback_data=f"reply_{user_id}"))
    return keyboard

def find_auto_reply(message_text):
    message_lower = message_text.lower()
    
    for pattern, reply in AUTO_REPLIES.items():
        if re.search(pattern, message_lower, re.IGNORECASE):
            return reply
    
    return None

@bot.message_handler(commands=['start'])
def start_command(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    welcome_text = (
        f"{SHOP_NAME} မှ ကြိုဆိုပါတယ်\n\n"
        f"👋 ဟယ်လို {user_name}!\n\n"
        "✨ ကျွန်ုပ်တို့တွင် အောက်ပါ Premium Digital Services များ ရရှိနိုင်ပါသည်:\n\n"
        "🔒 VPN Services - Premium VPN Keys\n"
        "🎮 Game Accounts - ML, PUBG, Magic Chess\n"
        "📱 Premium Apps - Spotify, Netflix, YouTube\n"
        "🎁 Gift Cards - Google Play, iTunes, Steam\n\n"
        "🚀 အထူးခြားချက်များ:\n"
        "• ⚡ Instant Delivery\n"
        "• 📞 24/7 Customer Support\n"
        "• 🛡️ Warranty System\n"
        "• 💳 Easy Payment\n\n"
        "💡 မှတ်ချက်: စျေးနှုန်းများကို Spoti4U App ထဲတွင်သာ ကြည့်ရှုနိုင်ပါသည်။ 📱\n\n"
        "✨ ကျေးဇူးပြု၍ အောက်ပါ option များမှ ရွေးချယ်ပါ သို့မဟုတ် သင့်မေးခွန်းကိုရိုက်ထည့်ပါ။"
    )
    
    if user_id == FOUNDER_ID:
        founder_text = (
            f"👑 Founder Admin Panel - မင်္ဂလာပါ {user_name}! 👑\n\n"
            "✅ Bot Status: Active & Running\n"
            "🤖 Auto-reply System: Enabled\n"
            "🔔 Customer Alerts: Active\n"
            "💾 Database: Connected\n\n"
            "⚡ Admin Commands:\n"
            "• /admin - Open Admin Panel\n"
            "• /pending - View Pending Messages\n"
            "• /stats - View Statistics\n"
            "• /broadcast - Send Broadcast\n\n"
            "💬 ကျေးဇူးပြု၍ Admin Panel ကိုအသုံးပြုပါ:"
        )
        bot.send_message(user_id, founder_text, reply_markup=create_admin_keyboard())
    else:
        bot.send_message(user_id, welcome_text, reply_markup=create_main_keyboard())
        
        db.save_message(user_id, user_name, "/start", "customer")
        
        try:
            notification = (
                f"🆕 New User Started Bot\n\n"
                f"👤 Name: {user_name}\n"
                f"🆔 ID: {user_id}\n"
                f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"✅ Status: Welcome message sent"
            )
            bot.send_message(FOUNDER_ID, notification)
        except Exception as e:
            logging.error(f"Failed to send founder notification: {e}")

@bot.message_handler(commands=['admin'])
def admin_command(message: Message):
    user_id = message.from_user.id
    
    if user_id == FOUNDER_ID:
        pending_count = len(db.get_pending_messages())
        
        admin_text = (
            f"👑 Spoti4U Admin Panel 👑\n\n"
            f"📊 Statistics:\n"
            f"• 📨 Pending Messages: {pending_count}\n"
            f"• ✅ Bot Status: Online\n"
            f"• 🤖 Auto-reply: Active\n"
            f"• 💾 Database: Connected\n\n"
            "⚡ Quick Actions:\n"
            "• 📨 Pending Messages - View unanswered messages\n"
            "• 📊 Statistics - View detailed stats\n"
            "• 🔍 Search User - Find user conversations\n"
            "• 📢 Broadcast - Send message to all users\n"
            "• 🔄 Refresh - Update statistics\n\n"
            "💬 Manual Reply Method:\n"
            "User ကို reply ပြန်ရန်:\n"
            "1. reply_123456789:message format ဖြင့်ရိုက်ပါ\n"
            "2. 123456789 = user_id, message = ပို့လိုသော message\n"
            "3. ဥပမာ: reply_5048500757:မင်္ဂလာပါ!\n\n"
            "✨ ကျေးဇူးပြု၍ option များမှ ရွေးချယ်ပါ:"
        )
        bot.send_message(user_id, admin_text, reply_markup=create_admin_keyboard())
    else:
        bot.send_message(user_id, "🚫 Permission Denied: This command is for admin only.")

@bot.message_handler(commands=['pending'])
def pending_command(message: Message):
    user_id = message.from_user.id
    
    if user_id == FOUNDER_ID:
        pending_messages = db.get_pending_messages()
        
        if not pending_messages:
            bot.send_message(user_id, "✅ No Pending Messages: All messages have been replied.", reply_markup=create_admin_keyboard())
            return
        
        pending_text = f"📨 Pending Messages - {len(pending_messages)} messages\n\n"
        
        for msg in pending_messages[:5]:
            msg_id, user_id, user_name, msg_text, msg_type, timestamp, replied, reply_text = msg
            pending_text += (
                f"👤 User: {user_name} (ID: {user_id})\n"
                f"⏰ Time: {timestamp}\n"
                f"💬 Message: {msg_text}\n"
                f"↩️ Reply: /reply_{user_id}\n"
                f"{'─'*40}\n"
            )
        
        if len(pending_messages) > 5:
            pending_text += f"\n📋 And {len(pending_messages) - 5} more messages..."
        
        pending_text += "\n💬 Reply Format: reply_USERID:your_message_here"
        
        bot.send_message(user_id, pending_text, reply_markup=create_admin_keyboard())
    else:
        bot.send_message(user_id, "🚫 Permission Denied: This command is for admin only.")

@bot.message_handler(commands=['stats'])
def stats_command(message: Message):
    user_id = message.from_user.id
    
    if user_id == FOUNDER_ID:
        pending_messages = db.get_pending_messages()
        stats_text = (
            f"📊 Bot Statistics\n\n"
            f"• 📨 Pending Messages: {len(pending_messages)}\n"
            f"• ✅ Bot Status: Online\n"
            f"• 🤖 Auto-reply: Active\n"
            f"• 👑 Founder ID: {FOUNDER_ID}\n"
            f"• 🏪 Shop: {SHOP_NAME}\n\n"
            f"🕒 Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        bot.send_message(user_id, stats_text, reply_markup=create_admin_keyboard())
    else:
        bot.send_message(user_id, "🚫 Permission Denied: This command is for admin only.")

@bot.message_handler(commands=['help'])
def help_command(message: Message):
    user_id = message.from_user.id
    
    if user_id == FOUNDER_ID:
        help_text = (
            f"🆘 Admin Help - {SHOP_NAME}\n\n"
            "⚡ Admin Commands:\n"
            "/admin - Open Admin Panel\n"
            "/pending - View Pending Messages\n"
            "/stats - View Statistics\n"
            "/broadcast - Send Broadcast Message\n\n"
            "💬 Manual Reply Methods:\n"
            "1. Format: reply_USERID:your_message\n"
            "   Example: reply_123456789:Hello!\n\n"
            "2. Use Pending Messages list\n"
            "   - Copy user ID from pending list\n"
            "   - Use reply format\n\n"
            "✨ Features:\n"
            "• 🤖 Auto-reply system\n"
            "• 💬 Conversation tracking\n"
            "• 👥 User management\n"
            "• 📢 Broadcast messages\n\n"
            "💡 Use Admin Panel for easy access:"
        )
        bot.send_message(user_id, help_text, reply_markup=create_admin_keyboard())
    else:
        help_text = (
            f"🆘 {SHOP_NAME} - အကူအညီ 🆘\n\n"
            "⚡ Available Commands:\n"
            "/start - Bot ကိုစတင်ရန်\n"
            "/help - အကူအညီရယူရန်\n\n"
            "🤖 Auto-reply Topics:\n"
            "• 🔒 VPN Services & Servers\n"
            "• 🎮 Game Accounts & Ranks\n"
            "• 📱 Premium Apps & Features\n"
            "• 🎁 Gift Cards & Denominations\n"
            "• 🛒 How to Buy & Payment\n"
            "• 🛡️ Warranty & Support\n\n"
            "💡 Quick Tips:\n"
            "• 💬 သင့်မေးခွန်းကိုရိုက်ထည့်ပါ (ဥပမာ: vpn, ml account, netflix)\n"
            "• ⌨️ Keyboard buttons ကိုသုံးပါ\n"
            "• 💵 စျေးနှုန်းများအတွက် App ကိုသုံးပါ\n\n"
            "✨ ကျေးဇူးပြု၍ အောက်ပါ option များမှ ရွေးချယ်ပါ:"
        )
        bot.send_message(user_id, help_text, reply_markup=create_main_keyboard())

def send_message_to_user(user_id, message_text, founder_name="Admin"):
    try:
        formatted_message = (
            f"💌 Message from {SHOP_NAME} 💌\n\n"
            f"{message_text}\n\n"
            f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"💬 Need more help? Just reply here!"
        )
        bot.send_message(user_id, formatted_message, reply_markup=create_main_keyboard())
        return True
    except Exception as e:
        logging.error(f"Failed to send message to user {user_id}: {e}")
        return False

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    message_text = message.text
    
    if user_id == FOUNDER_ID:
        if message_text == "📨 Pending Messages":
            pending_command(message)
            return
        elif message_text == "📊 Statistics":
            stats_command(message)
            return
        elif message_text == "🔍 Search User":
            bot.send_message(user_id, "🔍 Search User\n\n💡 Please use format: search_USERID\n📝 Example: search_5048500757", reply_markup=create_admin_keyboard())
            return
        elif message_text == "📢 Broadcast":
            bot.send_message(user_id, "📢 Broadcast Message\n\n💡 Please use format: broadcast:your_message_here", reply_markup=create_admin_keyboard())
            return
        elif message_text == "🔄 Refresh":
            admin_command(message)
            return
        elif message_text == "❌ Close Admin":
            bot.send_message(user_id, "✅ Admin Panel Closed\n\n💡 Use /admin to open again.", reply_markup=ReplyKeyboardRemove())
            return
        
        if message_text.startswith('reply_'):
            try:
                parts = message_text.split(':', 1)
                if len(parts) == 2:
                    user_id_part = parts[0].replace('reply_', '')
                    reply_message = parts[1]
                    
                    target_user_id = int(user_id_part)
                    
                    if send_message_to_user(target_user_id, reply_message, user_name):
                        bot.send_message(user_id, f"✅ Message Sent Successfully!\n\n👤 To: User ID {target_user_id}\n💬 Message: {reply_message}", reply_markup=create_admin_keyboard())
                        
                        db.save_message(user_id, user_name, f"Admin Reply: {reply_message}", "admin")
                    else:
                        bot.send_message(user_id, f"❌ Failed to send message\n\n👤 User ID: {target_user_id} might have blocked the bot.", reply_markup=create_admin_keyboard())
                else:
                    bot.send_message(user_id, "❌ Invalid Format\n\n💡 Use: reply_USERID:your_message", reply_markup=create_admin_keyboard())
            except ValueError:
                bot.send_message(user_id, "❌ Invalid User ID\n\n💡 User ID must be a number.", reply_markup=create_admin_keyboard())
            except Exception as e:
                bot.send_message(user_id, f"❌ Error: {str(e)}", reply_markup=create_admin_keyboard())
            return
        
        if message_text.startswith('search_'):
            try:
                target_user_id = int(message_text.replace('search_', ''))
                conversations = db.get_user_conversation(target_user_id)
                
                if not conversations:
                    bot.send_message(user_id, f"❌ No conversations found for User ID: {target_user_id}", reply_markup=create_admin_keyboard())
                    return
                
                search_text = f"🔍 Conversations with User ID: {target_user_id}\n\n"
                
                for conv in conversations[:10]:
                    msg_id, user_id, user_name, msg_text, msg_type, timestamp, replied, reply_text = conv
                    status = "✅" if replied else "⏳"
                    search_text += (
                        f"{status} {msg_type.upper()} - {timestamp}\n"
                        f"💬 {msg_text}\n"
                    )
                    if reply_text:
                        search_text += f"↩️ Reply: {reply_text}\n"
                    search_text += f"{'─'*40}\n"
                
                search_text += f"\n💬 Reply: reply_{target_user_id}:your_message"
                
                bot.send_message(user_id, search_text, reply_markup=create_admin_keyboard())
            except ValueError:
                bot.send_message(user_id, "❌ Invalid User ID\n\n💡 User ID must be a number.", reply_markup=create_admin_keyboard())
            return
        
        if message_text.startswith('broadcast:'):
            broadcast_message = message_text.replace('broadcast:', '').strip()
            if broadcast_message:
                bot.send_message(user_id, 
                    f"📢 Broadcast Message Ready\n\n"
                    f"💬 Message: {broadcast_message}\n\n"
                    f"💡 Note: Broadcast functionality requires user database setup.", 
                    reply_markup=create_admin_keyboard()
                )
            else:
                bot.send_message(user_id, "❌ Empty Broadcast Message", reply_markup=create_admin_keyboard())
            return
        
        bot.send_message(user_id, 
            "👑 Admin Command Received 👑\n\n"
            "✨ Available options:\n"
            "• Use Admin Panel buttons\n"
            "• /pending - View messages\n"
            "• reply_USERID:message - Send reply\n"
            "• search_USERID - Find user\n"
            "• broadcast:message - Broadcast", 
            reply_markup=create_admin_keyboard()
        )
        return
    
    handle_customer_message(message)

def handle_customer_message(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    message_text = message.text
    
    db.save_message(user_id, user_name, message_text, "customer")
    
    button_responses = {
        "🔒 VPN Services": AUTO_REPLIES[r'(vpn|ဗွီပီအန်|vpn service|vpn key)'],
        "🎮 Game Accounts": AUTO_REPLIES[r'(game account|ဂိမ်းအကောင့်|ml|pubg|mobile legends|magic chess|ဂိမ်း)'],
        "📱 Premium Apps": AUTO_REPLIES[r'(premium app|ပရီမီယံအက်ပ်|spotify|netflix|youtube|zoom|အက်ပ်)'],
        "🎁 Gift Cards": AUTO_REPLIES[r'(gift card|လက်ဆောင်ကတ်|google play|itunes|steam|wallet code|ဂစ်ကတ်)'],
        "🛒 How to Buy": AUTO_REPLIES[r'(ဘယ်လိုဝယ်ရမလဲ|ဝယ်ယူနည်း|ဘယ်လိုဝယ်မလဲ|how to buy|purchase|အသုံးပြုနည်း)'],
        "💰 Prices": AUTO_REPLIES[r'(စျေးနှုန်း|ဈေးနှုန်း|ဘယ်လောက်လဲ|price|cost|ဈေး)'],
        "🛡️ Warranty": AUTO_REPLIES[r'(အာမခံ|warranty|ပြန်လည်သွင်း|replace|အာမခံချက်)'],
        "📞 Contact": AUTO_REPLIES[r'(ဆက်သွယ်ရန်|contact|support|အကူအညီ|help|ကူညီ)'],
        "📲 Download App": AUTO_REPLIES[r'(app|application|အက်ပ်ဒေါင်းလုဒ်|download|အက်ပ်)']
    }
    
    if message_text in button_responses:
        bot.send_message(user_id, button_responses[message_text], reply_markup=create_main_keyboard())
        
        alert_message = (
            f"🔘 Button Click - Customer\n\n"
            f"👤 From: {user_name} (ID: {user_id})\n"
            f"🔘 Button: {message_text}\n"
            f"✅ Auto-reply sent successfully"
        )
    else:
        auto_reply = find_auto_reply(message_text)
        
        if auto_reply:
            bot.send_message(user_id, auto_reply, reply_markup=create_main_keyboard())
            
            alert_message = (
                f"🤖 Auto-Replied to Customer\n\n"
                f"👤 From: {user_name} (ID: {user_id})\n"
                f"💬 Message: {message_text}\n"
                f"✅ Auto-reply sent successfully"
            )
        else:
            alert_message = (
                f"📨 Customer Message - Need Manual Reply\n\n"
                f"👤 From: {user_name} (ID: {user_id})\n"
                f"💬 Message: {message_text}\n\n"
                f"⚠️ No auto-reply match found!\n"
                f"↩️ Reply: /reply_{user_id}"
            )
            
            bot.send_message(user_id, 
                "✅ ကျေးဇူးတင်ပါတယ်!\n\n"
                "💬 သင့်မေးခွန်းကို လက်ခံရရှိပါပြီ။\n"
                "👑 Founder မှ အမြန်ဆုံးပြန်လည်ဖြေကြားပေးပါမည်။\n\n"
                "⏳ ကျေးဇူးပြု၍ စောင့်ဆိုင်းပေးပါ။",
                reply_markup=create_main_keyboard()
            )
    
    try:
        bot.send_message(FOUNDER_ID, alert_message)
    except Exception as e:
        logging.error(f"Failed to send alert to founder: {e}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    callback_data = call.data
    
    responses = {
        "vpn_services": AUTO_REPLIES[r'(vpn|ဗွီပီအန်|vpn service|vpn key)'],
        "game_accounts": AUTO_REPLIES[r'(game account|ဂိမ်းအကောင့်|ml|pubg|mobile legends|magic chess|ဂိမ်း)'],
        "premium_apps": AUTO_REPLIES[r'(premium app|ပရီမီယံအက်ပ်|spotify|netflix|youtube|zoom|အက်ပ်)'],
        "gift_cards": AUTO_REPLIES[r'(gift card|လက်ဆောင်ကတ်|google play|itunes|steam|wallet code|ဂစ်ကတ်)'],
        "how_to_buy": AUTO_REPLIES[r'(ဘယ်လိုဝယ်ရမလဲ|ဝယ်ယူနည်း|ဘယ်လိုဝယ်မလဲ|how to buy|purchase|အသုံးပြုနည်း)'],
        "check_prices": AUTO_REPLIES[r'(စျေးနှုန်း|ဈေးနှုန်း|ဘယ်လောက်လဲ|price|cost|ဈေး)'],
        "warranty_info": AUTO_REPLIES[r'(အာမခံ|warranty|ပြန်လည်သွင်း|replace|အာမခံချက်)'],
        "contact_support": AUTO_REPLIES[r'(ဆက်သွယ်ရန်|contact|support|အကူအညီ|help|ကူညီ)']
    }
    
    if callback_data in responses:
        bot.send_message(user_id, responses[callback_data], reply_markup=create_main_keyboard())
    else:
        bot.send_message(user_id, "❌ Invalid selection. Please try again.", reply_markup=create_main_keyboard())
    
    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    print("🤖 Spoti4U Bot is running...")
    print("🏪 Shop: Spoti4U Premium Digital Services")
    print("👑 Admin System: Enabled")
    print("💾 Database: Connected")
    print("⌨️ Keyboard: Enabled")
    print("🤖 Auto-reply: Activated")
    print("💵 Prices: App Only")
    print("🔔 Founder Alerts: Active")
    print("✅ Bot Status: Professional & Ready!")
    bot.infinity_polling()