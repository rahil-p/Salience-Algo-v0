

#-----

class Stock:
    def __init__(self, type, symbol, cap):
        self.type = type
        self.symbol = symbol
        self.cap = cap
        self.power = cap
        self.owned = 0

    def update(type, quantity, price):
        self.power = update_power(type, quantity, price)
        self.owned = update_owned(type, quantity, price)

    def update_power(type, quantity, price):
        pass

    def update_owned(type, quantity, price):
        pass

#-----

def stock_requests():
    request_count = int(input('# of requests: '))
    requests = [stock_request() for x in range(request_count)]

    return requests

def stock_request():
    type = input("Type ('stocks' or 'crypto'): ")
    symbol = input('Symbol: ')
    cap = float(input('Cap (ie max spend in USD): '))

    return Stock(type, symbol, cap)

#-----
