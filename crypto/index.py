# crypto_whale_bot.py

import os
import time
import logging
import pandas as pd
import requests  # Thêm thư viện requests để gửi tin nhắn Telegram
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv
import schedule
import argparse

# Cấu hình logging với mã hóa UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crypto_whale_bot.log", encoding='utf-8'),  # Thêm encoding='utf-8'
        logging.StreamHandler()  # Console thường hỗ trợ Unicode, nhưng nếu gặp lỗi, bạn có thể thay đổi mã hóa
    ]
)

# Tải các biến môi trường từ tệp .env
load_dotenv()

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Kiểm tra sự tồn tại của API Key
if not API_KEY or not API_SECRET:
    logging.error("API Key hoặc Secret Key không được thiết lập. Vui lòng kiểm tra tệp .env.")
    exit(1)

# Khởi tạo client Binance
client = Client(API_KEY, API_SECRET)

# Đọc các ngưỡng từ biến môi trường
BTC_THRESHOLD = float(os.getenv('BTCUSDT_THRESHOLD', 100))
ETH_THRESHOLD = float(os.getenv('ETHUSDT_THRESHOLD', 50))
DEFAULT_THRESHOLD = float(os.getenv('DEFAULT_THRESHOLD', 100))

# Đọc thông tin Telegram từ biến môi trường
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Hàm gửi tin nhắn qua Telegram
def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("Telegram Bot Token hoặc Chat ID không được thiết lập. Vui lòng kiểm tra tệp .env.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"  # Sử dụng Markdown để định dạng tin nhắn (có thể thay đổi tùy ý)
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            logging.error(f"Lỗi khi gửi tin nhắn Telegram: {response.text}")
    except Exception as e:
        logging.error(f"Lỗi không xác định khi gửi tin nhắn Telegram: {e}")

# Hàm lấy giao dịch gần đây
def get_recent_trades(symbol, limit=1000):
    try:
        trades = client.get_recent_trades(symbol=symbol, limit=limit)
        df = pd.DataFrame(trades)
        # Chuyển đổi kiểu dữ liệu
        df['qty'] = df['qty'].astype(float)
        df['price'] = df['price'].astype(float)
        df['isBuyerMaker'] = df['isBuyerMaker'].astype(bool)
        return df
    except BinanceAPIException as e:
        logging.error(f"Lỗi Binance API khi lấy giao dịch cho {symbol}: {e}")
    except BinanceRequestException as e:
        logging.error(f"Lỗi yêu cầu Binance khi lấy giao dịch cho {symbol}: {e}")
    except Exception as e:
        logging.error(f"Lỗi không xác định khi lấy giao dịch cho {symbol}: {e}")
    return pd.DataFrame()

# Hàm xác định whales và thêm cột direction
def detect_whales(df, threshold=100, symbol=''):
    """
    Xác định các giao dịch lớn dựa trên ngưỡng kích thước.
    threshold: Kích thước giao dịch tối thiểu (số lượng coin).
    """
    df['is_whale'] = df['qty'] >= threshold
    whales = df[df['is_whale']].copy()
    # Thêm cột direction dựa trên isBuyerMaker
    whales['direction'] = whales['isBuyerMaker'].apply(lambda x: 'SELL' if x else 'BUY')
    
    # Ghi log số giao dịch lớn được phát hiện
    logging.info(f"Phát hiện {len(whales)} giao dịch lớn trong {threshold} {symbol}.")
    
    return whales

# Hàm lấy thông tin vị thế Futures (Long/Short)
def get_futures_positions(symbol):
    try:
        positions = client.futures_position_information(symbol=symbol)
        df_positions = pd.DataFrame(positions)
        # Chuyển đổi kiểu dữ liệu
        df_positions['positionAmt'] = df_positions['positionAmt'].astype(float)
        df_positions['entryPrice'] = df_positions['entryPrice'].astype(float)
        df_positions['unRealizedProfit'] = df_positions['unRealizedProfit'].astype(float)
        
        # Ghi log để kiểm tra dữ liệu vị thế
        logging.info(f"Vị thế cho {symbol}:\n{df_positions}")
        
        return df_positions
    except BinanceAPIException as e:
        logging.error(f"Lỗi Binance API khi lấy vị thế cho {symbol}: {e}")
    except BinanceRequestException as e:
        logging.error(f"Lỗi yêu cầu Binance khi lấy vị thế cho {symbol}: {e}")
    except Exception as e:
        logging.error(f"Lỗi không xác định khi lấy vị thế cho {symbol}: {e}")
    return pd.DataFrame()

# Hàm phân tích tỷ lệ Long/Short
def analyze_long_short(df_positions):
    """
    Phân tích tỷ lệ Long và Short từ DataFrame vị thế.
    """
    long_positions = df_positions[df_positions['positionAmt'] > 0]
    short_positions = df_positions[df_positions['positionAmt'] < 0]
    total_long = long_positions['positionAmt'].sum()
    total_short = abs(short_positions['positionAmt'].sum())
    
    # Ghi log để kiểm tra các vị thế Long và Short
    logging.info(f"Long positions:\n{long_positions}")
    logging.info(f"Short positions:\n{short_positions}")
    logging.info(f"Tổng Long: {total_long} | Tổng Short: {total_short}")
    
    return total_long, total_short

# Hàm gửi thông báo (In ra console và gửi qua Telegram)
def send_notification(symbol, whales, total_long, total_short):
    # Tạo message
    message = f"===== {symbol} =====\n"
    message += f"Phát hiện {len(whales)} giao dịch lớn (>= threshold).\n\n"
    message += "Chi tiết giao dịch:\n"
    for index, row in whales.iterrows():
        message += f"• ID: {row['id']}, Price: {row['price']}, Quantity: {row['qty']}, Direction: *{row['direction']}*\n"
    message += f"\nTổng Long: {total_long} | Tổng Short: {total_short}\n"
    message += "====================\n"
    
    # Ghi log
    logging.info(message)
    
    # Gửi tin nhắn qua Telegram
    send_telegram_message(message)

# Hàm chính để theo dõi một đồng coin
def monitor_symbol(symbol, trade_threshold=100):
    logging.info(f"Bắt đầu theo dõi {symbol} với ngưỡng giao dịch: {trade_threshold}...")
    df_trades = get_recent_trades(symbol)
    if df_trades.empty:
        logging.warning(f"Không có dữ liệu giao dịch cho {symbol}.")
        return
    whales = detect_whales(df_trades, threshold=trade_threshold, symbol=symbol)
    if not whales.empty:
        logging.info(f"Phát hiện {len(whales)} giao dịch lớn cho {symbol}.")
        df_positions = get_futures_positions(symbol)
        if df_positions.empty:
            logging.warning(f"Không có dữ liệu vị thế cho {symbol}.")
            return
        total_long, total_short = analyze_long_short(df_positions)
        send_notification(symbol, whales, total_long, total_short)
    else:
        logging.info(f"Không phát hiện giao dịch lớn nào cho {symbol}.")

# Hàm thiết lập các đồng coin cần theo dõi
def get_symbols_to_monitor():
    # Lấy các đồng coin từ biến môi trường
    monitor_symbols_env = os.getenv('MONITOR_SYMBOLS', '').strip()
    if monitor_symbols_env:
        # Nếu biến MONITOR_SYMBOLS được thiết lập, sử dụng danh sách này
        symbols = [symbol.strip().upper() for symbol in monitor_symbols_env.split(',') if symbol.strip()]
        logging.info(f"Đồng coin được chỉ định để theo dõi: {', '.join(symbols)}")
        return symbols
    else:
        # Nếu không, theo dõi toàn bộ đồng coin kết thúc bằng 'USDT'
        try:
            exchange_info = client.get_exchange_info()
            symbols = [s['symbol'] for s in exchange_info['symbols'] if s['status'] == 'TRADING']
            # Lọc các đồng futures (kết thúc bằng 'USDT' hoặc tùy theo nhu cầu)
            symbols_futures = [s for s in symbols if s.endswith('USDT')]
            logging.info(f"Đang theo dõi toàn bộ các đồng coin kết thúc bằng 'USDT' ({len(symbols_futures)} đồng).")
            return symbols_futures
        except BinanceAPIException as e:
            logging.error(f"Lỗi Binance API khi lấy thông tin sàn: {e}")
        except BinanceRequestException as e:
            logging.error(f"Lỗi yêu cầu Binance khi lấy thông tin sàn: {e}")
        except Exception as e:
            logging.error(f"Lỗi không xác định khi lấy thông tin sàn: {e}")
        return []

# Hàm công việc định kỳ
def job():
    logging.info("===== Bắt đầu công việc theo dõi =====")
    symbols = get_symbols_to_monitor()
    if not symbols:
        logging.warning("Không tìm thấy đồng coin để theo dõi.")
        return
    for symbol in symbols:
        # Tùy chỉnh ngưỡng cho từng đồng coin nếu cần
        if symbol == 'BTCUSDT':
            threshold = BTC_THRESHOLD
        elif symbol == 'ETHUSDT':
            threshold = ETH_THRESHOLD
        else:
            threshold = DEFAULT_THRESHOLD  # Mặc định
        monitor_symbol(symbol, trade_threshold=threshold)  # Bạn có thể điều chỉnh ngưỡng tại đây
        time.sleep(0.5)  # Giảm tốc độ gửi yêu cầu để tuân thủ giới hạn API
    logging.info("===== Kết thúc công việc theo dõi =====\n")

# Hàm để parse đối số dòng lệnh (tuỳ chọn)
def parse_arguments():
    parser = argparse.ArgumentParser(description="Crypto Whale Bot")
    parser.add_argument(
        '--symbols',
        type=str,
        help="Danh sách các đồng coin cần theo dõi, cách nhau bằng dấu phẩy (ví dụ: BTCUSDT,ETHUSDT). Nếu không chỉ định, bot sẽ theo dõi toàn bộ các đồng coin kết thúc bằng 'USDT'."
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    # Nếu người dùng cung cấp các đồng coin qua dòng lệnh, ghi đè lên biến môi trường
    if args.symbols:
        os.environ['MONITOR_SYMBOLS'] = args.symbols
        logging.info(f"Đồng coin được chỉ định qua dòng lệnh: {args.symbols}")

    logging.info("===== Khởi động Crypto Whale Bot =====")
    # Chạy công việc ngay khi khởi động
    job()
    while True:
        schedule.run_pending()
        time.sleep(5)
