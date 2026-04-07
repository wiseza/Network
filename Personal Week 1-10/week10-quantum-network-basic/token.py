#token.py
import time
from config import TOKEN_EXPIRY

class Token:
    def __init__(self, message):
        self.message = message
        self.read = False
        self.timestamp = time.time()

    def is_valid(self):
        return (time.time() - self.timestamp) <= TOKEN_EXPIRY

    def read_token(self):
        # ❌ อ่านไม่ได้ถ้าใช้แล้ว หรือหมดอายุ
        if self.read:
            return None

        if not self.is_valid():
            return None

        self.read = True
        return self.message

