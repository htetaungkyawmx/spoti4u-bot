import logging
import re
import telebot
from telebot.types import Message

BOT_TOKEN = "8540709881:AAHGbtI_OzPC_LOo84VEz4Oo-2f_hZPrRQs"
FOUNDER_ID = 5048500757
SHOP_NAME = "Spoti4U Premium Digital Services"

# Bot create
bot = telebot.TeleBot(BOT_TOKEN)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Auto-reply responses in Myanmar language
AUTO_REPLIES = {
    # VPN Services
    r'(vpn|ဗွီပီအန်|vpn service)': 
        "🔒 **VPN Services**\n\n"
        "• Premium VPN Keys\n"
        "• High Speed Connection\n"
        "• Multiple Server Locations\n"
        "• 30 Days Warranty\n\n"
        "စျေးနှုန်းအတွက် Spoti4U App ထဲတွင်ကြည့်ရှုနိုင်ပါသည်။",

    # Game Accounts
    r'(game account|ဂိမ်းအကောင့်|ml|pubg|mobile legends)': 
        "🎮 **Game Accounts**\n\n"
        "• Mobile Legends Accounts\n"
        "• PUBG Mobile Accounts\n"
        "• Magic Chess Accounts\n"
        "• Various Ranks Available\n\n"
        "စျေးနှုန်းအတွက် Spoti4U App ထဲတွင်ကြည့်ရှုနိုင်ပါသည်။",

    # Premium Apps
    r'(premium app|ပရီမီယံအက်ပ်|spotify|netflix|youtube)': 
        "📱 **Premium Apps**\n\n"
        "• Spotify Premium\n"
        "• Netflix Premium\n"
        "• YouTube Premium\n"
        "• Zoom Premium\n\n"
        "စျေးနှုန်းအတွက် Spoti4U App ထဲတွင်ကြည့်ရှုနိုင်ပါသည်။",

    # Gift Cards
    r'(gift card|လက်ဆောင်ကတ်|google play|itunes|steam)': 
        "🎁 **Gift Cards**\n\n"
        "• Google Play Gift Cards\n"
        "• iTunes Gift Cards\n"
        "• Steam Wallet Codes\n"
        "• Various Denominations\n\n"
        "စျေးနှုန်းအတွက် Spoti4U App ထဲတွင်ကြည့်ရှုနိုင်ပါသည်။",

    # Service questions
    r'(ဘယ်လိုဝယ်ရမလဲ|ဝယ်ယူနည်း|ဘယ်လိုဝယ်မလဲ|how to buy|purchase)': 
        "🛒 **ဝယ်ယူနည်း**\n\n"
        "1. Spoti4U App မှ လိုချင်သော service ကိုရွေးချယ်ပါ\n"
        "2. KBZ Pay, Wave Pay ဖြင့်ငွေလွှဲပါ\n"
        "3. ဝယ်ယူလိုသည့် product ကိုရွေးချယ်ဝယ်ယူပါ\n"
        "4. ချက်ချင်း digital product ရရှိမည်\n\n"
        "စျေးနှုန်းများကို App ထဲတွင်ကြည့်ရှုနိုင်ပါသည်။",

    r'(စျေးနှုန်း|ဈေးနှုန်း|ဘယ်လောက်လဲ|price|cost)': 
        "💰 **စျေးနှုန်းများ**\n\n"
        "စျေးနှုန်းများကို Spoti4U App ထဲတွင်သာ ကြည့်ရှုနိုင်ပါသည်။\n\n"
        "• App ထဲမှာ Real-time စျေးနှုန်းများ\n"
        "• အချိန်နှင့်တစ်ပြေးညီ Update\n"
        "• Promotion နှင့် Discount များ\n\n"
        "ကျေးဇူးပြု၍ Spoti4U App ကိုသုံး၍ စျေးနှုန်းများကိုကြည့်ရှုပါ။",

    r'(အာမခံ|warranty|ပြန်လည်သွင်း|replace)': 
        "✅ **အာမခံစနစ်**\n\n"
        "• Digital Products - 30 ရက်အာမခံ\n"
        "• VPN Services - 30 ရက်အာမခံ\n"
        "• Game Accounts - 7 ရက်အာမခံ\n"
        "• ပြဿနာရှိပါက 24 နာရီအတွင်းအခမဲ့ပြန်လည်သွင်းပေးခြင်း",

    r'(ငွေလွှဲနည်း|payment|pay|KBZ|Wave)': 
        "💳 **ငွေလွှဲနည်း**\n\n"
        "• KBZ Pay\n"
        "• Wave Pay\n\n"
        "ငွေဖြည့်ရန် App ထဲမှာ Wallet Top-up ကိုသုံးပါ။",

    # App download and features
    r'(app|application|အက်ပ်ဒေါင်းလုဒ်|download)': 
        "📱 **Spoti4U App**\n\n"
        "Spoti4U App ထဲတွင် အောက်ပါဝန်ဆောင်မှုများ ရရှိနိုင်ပါသည်:\n\n"
        "• VPN Services\n"
        "• Game Accounts\n"
        "• Premium Apps\n"
        "• Gift Cards\n"
        "• Digital Products\n\n"
        "စျေးနှုန်းများ၊ ဝန်ဆောင်မှုများနှင့် Promotion များကို App ထဲတွင်ကြည့်ရှုနိုင်ပါသည်။",

    # Balance and wallet
    r'(လက်ကျန်|balance|ပိုက်ဆံအိတ်|wallet)': 
        "💰 **Wallet System**\n\n"
        "Spoti4U App ထဲတွင် Wallet System ပါရှိပါသည်:\n\n"
        "• ငွေဖြည့်သွင်းနိုင်ခြင်း\n"
        "• လက်ကျန်ကြည့်ရှုနိုင်ခြင်း\n"
        "• အလွယ်တကူဝယ်ယူနိုင်ခြင်း\n"
        "• Transaction History ကြည့်ရှုနိုင်ခြင်း",

    # Server information
    r'(server|ဆာဗာ|brazil|philippines)': 
        "🌐 **Server Information**\n\n"
        "• Brazil Server\n"
        "• Philippines Server\n"
        "• Multiple Locations\n"
        "• High Speed Connection\n\n"
        "VPN service များအတွက် server များစွာရှိပါသည်။",

    # General greeting
    r'(မင်္ဂလာပါ|hello|hi|နေကောင်းလား)': 
        f"မင်္ဂလာပါ! {SHOP_NAME} မှ ကြိုဆိုပါတယ်! 😊\n\n"
        "ကျေးဇူးပြု၍ သင့်မေးခွန်းကိုမေးပါ။\n"
        "သို့မဟုတ် /help ကိုနှိပ်၍ အကူအညီယူနိုင်ပါသည်။",

    # New services
    r'(ဝန်ဆောင်မှု|services|ဘာတွေရလဲ)': 
        "🛍️ **ရနိုင်သော ဝန်ဆောင်မှုများ**\n\n"
        "• 🔒 VPN Services\n"
        "• 🎮 Game Accounts\n"
        "• 📱 Premium Apps\n"
        "• 🎁 Gift Cards\n\n"
        "စျေးနှုန်းများကို Spoti4U App ထဲတွင်ကြည့်ရှုနိုင်ပါသည်။"
}

def find_auto_reply(message_text):
    """Find matching auto-reply for the message"""
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
        f"🎉 **{SHOP_NAME} မှ ကြိုဆိုပါတယ်!** 🎉\n\n"
        f"ဟယ်လို {user_name}!\n\n"
        "ကျွန်ုပ်တို့တွင် အောက်ပါ Digital Services များ ရရှိနိုင်ပါသည်:\n\n"
        "• 🔒 **VPN Services** - Premium VPN Keys\n"
        "• 🎮 **Game Accounts** - ML, PUBG, Magic Chess\n"
        "• 📱 **Premium Apps** - Spotify, Netflix, YouTube\n"
        "• 🎁 **Gift Cards** - Google Play, iTunes, Steam\n\n"
        "**မှတ်ချက်:** စျေးနှုန်းများကို Spoti4U App ထဲတွင်သာ ကြည့်ရှုနိုင်ပါသည်။\n\n"
        "မေးခွန်းရှိပါက ရိုက်ထည့်မေးမြန်းနိုင်ပါသည်။\n"
        "သို့မဟုတ် /help ကိုနှိပ်၍ အကူအညီယူနိုင်ပါသည်။"
    )
    
    if user_id == FOUNDER_ID:
        bot.reply_to(message, f"👑 **Founder မင်္ဂလာပါ!** {user_name}!")
    else:
        bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def help_command(message: Message):
    help_text = (
        f"🆘 **{SHOP_NAME} - အကူအညီ**\n\n"
        "**အသုံးပြုနည်း:**\n"
        "/start - Bot ကိုစတင်ရန်\n"
        "/help - အကူအညီရယူရန်\n"
        "/services - ဝန်ဆောင်မှုများကြည့်ရန်\n"
        "/howtobuy - ဝယ်ယူနည်း\n\n"
        "**အလိုအလျောက်ဖြေကြားခြင်း:**\n"
        "• VPN Services\n"
        "• Game Accounts\n"
        "• Premium Apps\n"
        "• Gift Cards\n"
        "• ဝယ်ယူနည်း\n"
        "• ငွေလွှဲနည်း\n"
        "• အာမခံ\n\n"
        "**မှတ်ချက်:** စျေးနှုန်းများကို Spoti4U App ထဲတွင်သာ ကြည့်ရှုနိုင်ပါသည်။\n\n"
        "မေးခွန်းရှိပါက ရိုက်ထည့်မေးမြန်းနိုင်ပါသည်။"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['services'])
def services_command(message: Message):
    services_text = (
        "🛍️ **ဝန်ဆောင်မှုများ**\n\n"
        "**🔒 VPN Services:**\n"
        "• Premium VPN Keys\n"
        "• High Speed Connection\n"
        "• Multiple Server Locations\n"
        "• 30 Days Warranty\n\n"
        "**🎮 Game Accounts:**\n"
        "• Mobile Legends Accounts\n"
        "• PUBG Mobile Accounts\n"
        "• Magic Chess Accounts\n"
        "• Various Ranks Available\n\n"
        "**📱 Premium Apps:**\n"
        "• Spotify Premium\n"
        "• Netflix Premium\n"
        "• YouTube Premium\n"
        "• Zoom Premium\n\n"
        "**🎁 Gift Cards:**\n"
        "• Google Play Gift Cards\n"
        "• iTunes Gift Cards\n"
        "• Steam Wallet Codes\n"
        "• Various Denominations\n\n"
        "**ဝန်ဆောင်မှုအာမခံ:**\n"
        "• 30 Days Warranty for Digital Products\n"
        "• 24/7 Customer Support\n"
        "• Free Replacement within 24 hours\n\n"
        "**မှတ်ချက်:** စျေးနှုန်းများကို Spoti4U App ထဲတွင်သာ ကြည့်ရှုနိုင်ပါသည်။"
    )
    bot.reply_to(message, services_text)

@bot.message_handler(commands=['howtobuy'])
def howtobuy_command(message: Message):
    howtobuy_text = (
        "🛒 **ဝယ်ယူနည်း**\n\n"
        "**အဆင့် ၁ - Spoti4U App ကိုဖွင့်ပါ**\n"
        "Spoti4U App မှ လိုချင်သော service ကိုရွေးချယ်ပါ\n\n"
        "**အဆင့် ၂ - ငွေဖြည့်သွင်းပါ**\n"
        "• Wallet ထဲသို့ငွေဖြည့်သွင်းပါ\n"
        "• KBZ Pay သို့မဟုတ် Wave Pay သုံးနိုင်သည်\n\n"
        "**အဆင့် ၃ - Product ဝယ်ယူပါ**\n"
        "• လိုချင်သော product ကိုရွေးချယ်ဝယ်ယူပါ\n"
        "• ချက်ချင်း digital product ရရှိမည်\n\n"
        "**အဆင့် ၄ - Product ရယူပါ**\n"
        "• VPN Configuration\n"
        "• Game Account Details\n"
        "• Premium App Accounts\n"
        "• Gift Card Codes\n\n"
        "**အာမခံ:**\n"
        "• 30 ရက်အာမခံ (Digital Products)\n"
        "• 7 ရက်အာမခံ (Game Accounts)\n"
        "• အခမဲ့ပြန်လည်သွင်းခြင်း\n"
        "• 24/7 ဝန်ဆောင်မှု\n\n"
        "**မှတ်ချက်:** စျေးနှုန်းများကို Spoti4U App ထဲတွင်သာ ကြည့်ရှုနိုင်ပါသည်။"
    )
    bot.reply_to(message, howtobuy_text)

@bot.message_handler(func=lambda message: True)
def handle_customer_message(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    message_text = message.text
    
    # Founder မဟုတ်ရင် (Customer ဆိုရင်)
    if user_id != FOUNDER_ID:
        # Auto-reply ရှာမယ်
        auto_reply = find_auto_reply(message_text)
        
        if auto_reply:
            # Auto-reply ရှိရင် ဖြေပေးမယ်
            bot.reply_to(message, auto_reply)
            
            # Founder ဆီကိုလည်း notification ပို့မယ်
            alert_message = (
                f"🔔 **Auto-Replied to Customer**\n\n"
                f"From: {user_name} (ID: {user_id})\n"
                f"Message: {message_text}\n"
                f"Auto-reply sent successfully! ✅"
            )
        else:
            # Auto-reply မရှိရင် Founder ဆီပို့မယ်
            alert_message = (
                f"🔔 **Customer Message - Need Manual Reply**\n\n"
                f"From: {user_name} (ID: {user_id})\n"
                f"Message: {message_text}\n\n"
                f"⚠️ No auto-reply match found!"
            )
            
            # Customer ကိုလည်း notification ပို့မယ်
            bot.reply_to(message, 
                "✔️ ကျေးဇူးတင်ပါတယ်! သင့်မေးခွန်းကို လက်ခံရရှိပါပြီ။ "
                "Founder မှ အမြန်ဆုံးပြန်လည်ဖြေကြားပေးပါမည်။"
            )
        
        # Founder ဆီကို alert ပို့မယ်
        try:
            bot.send_message(FOUNDER_ID, alert_message)
        except Exception as e:
            logging.error(f"Failed to send alert to founder: {e}")
    
    # Founder ကပို့တဲ့ message (manual reply အတွက်)
    else:
        bot.reply_to(message,
            "👑 Founder: သင့်ရဲ့ message ကို လက်ခံရရှိပါပြီ။ "
            "Customer ကို manual reply ပို့ရန် ဤ bot မှတစ်ဆင့်မပို့နိုင်သေးပါ။ "
            "Direct ဆက်သွယ်ပါ။"
        )

if __name__ == "__main__":
    print("🤖 Spoti4U Bot is running...")
    print("📍 Shop: Spoti4U Premium Digital Services")
    print("✅ Auto-reply system activated!")
    print("💰 Prices are only available in the App")
    bot.infinity_polling()