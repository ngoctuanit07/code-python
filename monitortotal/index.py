import requests
import time

# Định nghĩa các URL API để lấy thông tin vốn hóa thị trường
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/global"

# Ngưỡng vốn hóa để xác định "Altcoin Season"
ALERT_THRESHOLD = 1.2 * 10**12  # 1.2 nghìn tỷ USD

# Cấu hình thông tin Telegram Bot
TELEGRAM_TOKEN = '6594741806:AAHLOUUC2tTsW6x2cZeDsONbXz0Nk0XkpIM'  # Thay YOUR_TELEGRAM_BOT_TOKEN bằng token của bạn
CHAT_ID = '-4290435424'  # Thay YOUR_CHAT_ID bằng chat ID của bạn

def send_telegram_message(message):
    """
    Hàm gửi thông báo đến Telegram qua bot.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Thông báo Telegram đã được gửi.")
        else:
            print(f"Lỗi khi gửi thông báo Telegram: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Lỗi kết nối Telegram: {e}")

def get_market_data():
    """
    Hàm lấy dữ liệu vốn hóa từ CoinGecko API.
    Trả về vốn hóa của Bitcoin và Altcoin.
    """
    try:
        response = requests.get(COINGECKO_API_URL)
        if response.status_code == 200:
            data = response.json()
            total_market_cap = data['data']['total_market_cap']['usd']
            btc_market_cap = data['data']['market_cap_percentage']['btc'] / 100 * total_market_cap
            total2_market_cap = total_market_cap - btc_market_cap

            return btc_market_cap, total2_market_cap
        else:
            print(f"Lỗi khi lấy dữ liệu: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Lỗi kết nối đến API: {e}")
        return None, None

def track_market_cap():
    """
    Theo dõi tỷ lệ vốn hóa thị trường và thông báo nếu Total2 vượt ngưỡng xác định.
    """
    while True:
        btc_market_cap, total2_market_cap = get_market_data()
        if btc_market_cap and total2_market_cap:
            print(f"BTC Market Cap: {btc_market_cap / 10**12:.2f} nghìn tỷ USD")
            print(f"Altcoin Market Cap (Total2): {total2_market_cap / 10**12:.2f} nghìn tỷ USD")
            
            # Kiểm tra điều kiện "Altcoin Season"
            if total2_market_cap > btc_market_cap:
                message = f"🔥🔥 *Altcoin Season đang đến!* 🔥🔥\n\n" \
                          f"Vốn hóa thị trường Altcoin (TOTAL2): {total2_market_cap / 10**12:.2f} nghìn tỷ USD vượt ngưỡng 1.2 nghìn tỷ USD!\n\n" \
                          f"BTC Market Cap: {btc_market_cap / 10**12:.2f} nghìn tỷ USD"
                print(message)
                send_telegram_message(message)
            else:
                print("BTC vẫn đang chi phối thị trường. Chưa phải là mùa Altcoin.")

        # Tạm dừng trong 60 giây trước khi lấy dữ liệu tiếp theo
        time.sleep(60)

# Chạy script theo dõi
track_market_cap()
