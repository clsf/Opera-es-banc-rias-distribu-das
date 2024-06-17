import time

class Account:
    def __init__(self, accountNumber, balance, password):
        self.accountNumber = accountNumber
        self.balance = balance
        self.holdBalance = 0
        self.version = int(time.time() * 1000)
        self.password = password
        