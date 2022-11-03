import pyupbit
import numpy as np



#OHLCV(open, high, low, close, volume)은 당일 시가 고가 저가 종가 거래량에 대한 데이터이다 / cuont 7은 7일동안의 데이터
df = pyupbit.get_ohlcv("KRW-BTC", count=7)


#변동폭 * k 계산, (고가-저가) * k값 // range(변동폭*k)
df['range'] = (df['high'] - df['low']) * 0.5


#target(매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1)) // target(매수가)
df['target'] = df['open'] + df['range'].shift(1)


## np.where(조건문, 참일때 값, 거짓일때 값) // ror(수익률)
df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'], 
                     1)


#누적 곱 계산(cumprod) => 누적 수익률 // hpr(누적수익률)
df['hpr'] = df['ror'].cumprod()


#Draw Down 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100) // dd(낙폭락)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100


#MDD 계산
print("MDD(%): ", df['dd'].max())


#엑셀로 출력
df.to_excel("dd.xlsx")


# 또한 가장 좋은 K값을 구하는 코드도 있다. https://wikidocs.net/21891 7-2에 있음 참고