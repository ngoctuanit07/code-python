from pytrends.request import TrendReq
import pandas as pd

def check_keyword_competition(keywords):
    # Khởi tạo pytrends
    pytrends = TrendReq(hl='en-US', tz=360)
    
    # Danh sách từ khóa cần kiểm tra
    keyword_list = keywords
    
    # Xây dựng payload và lấy dữ liệu từ Google Trends
    pytrends.build_payload(keyword_list, cat=0, timeframe='today 12-m', geo='', gprop='')
    
    # Lấy dữ liệu về mức độ quan tâm
    interest_over_time_df = pytrends.interest_over_time()
    
    if not interest_over_time_df.empty:
        interest_over_time_df = interest_over_time_df.drop(labels=['isPartial'], axis='columns')
        print(interest_over_time_df)
    else:
        print("No data found for the given keywords.")

# List các từ khóa bạn muốn kiểm tra
keywords_to_check = ['in túi giấy cao cấp', 'in túi giấy đựng quà tặng', 'túi giấy in logo công ty','in hộp đựng bánh kẹo']

# Gọi hàm để kiểm tra độ cạnh tranh của từ khóa
check_keyword_competition(keywords_to_check)
