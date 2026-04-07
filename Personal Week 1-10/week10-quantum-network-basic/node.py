#node.py
import socket
import threading
import time
import sys

from config import HOST, BUFFER_SIZE, UPDATE_INTERVAL
from token import Token

BASE_PORT = int(sys.argv[1])
PEER_PORTS = [int(p) for p in sys.argv[2:]]

token_queue = []


def send_token(peer_port, token):
    # ❌ ไม่ส่ง token ที่หมดอายุ
    if not token.is_valid():
        print(f"[NODE {BASE_PORT}] Token expired, not sending")
        return False

    # ❌ กัน loop
    if f"via {BASE_PORT}" in token.message:
        return False

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))

        new_msg = f"{token.message} -> via {BASE_PORT}"
        s.sendall(new_msg.encode())
        s.close()

        print(f"[NODE {BASE_PORT}] Sent token to {peer_port}")
        return True

    except (ConnectionRefusedError, socket.timeout):
        print(f"[NODE {BASE_PORT}] Failed to send to {peer_port}")
        return False


def forward_loop():
    while True:
        for token in token_queue[:]:

            # ❌ ลบทิ้งถ้า token หมดอายุ
            if not token.is_valid():
                print(f"[NODE {BASE_PORT}] Dropped expired token")
                token_queue.remove(token)
                continue

            for peer in PEER_PORTS:
                if send_token(peer, token):
                    token_queue.remove(token)
                    break

        time.sleep(UPDATE_INTERVAL)


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, BASE_PORT))
    server.listen()

    print(f"[NODE {BASE_PORT}] Listening...")

    while True:
        conn, addr = server.accept()
        data = conn.recv(BUFFER_SIZE).decode()

        token = Token(data)

        message = token.read_token()

        if message:
            print(f"[NODE {BASE_PORT}] Received & consumed: {message}")

            # 🔥 quantum behavior:
            # อ่านแล้ว = state collapse
            # แต่ยัง forward "state ใหม่" ต่อได้
            token_queue.append(token)

        else:
            print(f"[NODE {BASE_PORT}] Token invalid / expired / used")

        conn.close()


if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # 🚀 initial token
    initial_token = Token(f"Quantum token from {BASE_PORT}")
    token_queue.append(initial_token)

    while True:
        time.sleep(1)