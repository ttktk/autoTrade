import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet

access = "UByx53xVJmcPL1yDxX6ODxGF8wR02dGHSEV5gVBD"
secret = "WL7JbC98DucR8Ptx7wm8JISf8bOd68KTa09pOfdd"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute15", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)         #업비트 API에서의 차트는 일봉으로 9시로 표기가 됨 (즉 day는 일봉으로) 
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

predicted_close_price = 0               #여기에 당일 종가 예측값 저장

#구글 코랩에서 인공지능 모델 구현한 코드
def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue
predict_price("KRW-BTC")
schedule.every().hour.do(lambda: predict_price("KRW-BTC"))

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("@@@@ 자동매매 시작 @@@@")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()
        #9 : 00 < 현재 < 20 : 59 : 50 까지 해당하는 시간 을 만족하면 매수 목표값 설정
        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and current_price < predicted_close_price:          #한 시간에 한번씩 업데이트 되는 predicted_close_price(종가의 가격)이 더 높을 경우 매수
                krw = get_balance("KRW")
                if krw > 5000:      #최소 주문 가능 금액인 5000원 설정 5000원 이상이면 사게끔
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)           #수수로 0.05% 고려
        else:
            btc = get_balance("BTC")
            if btc > 0.00002:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)