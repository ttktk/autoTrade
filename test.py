import pyupbit


#로그인
access = "UByx53xVJmcPL1yDxX6ODxGF8wR02dGHSEV5gVBD"          
secret = "WL7JbC98DucR8Ptx7wm8JISf8bOd68KTa09pOfdd"          
upbit = pyupbit.Upbit(access, secret)



#잔고 조회
print(upbit.get_balance("KRW-BTC"))     # 비트코인 가격 조회
print(upbit.get_balance("KRW-XRP"))     # 리플 가격 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회
