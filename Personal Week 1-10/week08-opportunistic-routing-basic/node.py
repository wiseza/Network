import socket
import threading
import time
import sys

# ---------------------------
# CONFIG (รวมไว้ในไฟล์เดียว)
HOST = "127.0.0.1"
BUFFER_SIZE = 1024
FORWARD_THRESHOLD = 0.5
UPDATE_INTERVAL = 5

# ---------------------------
# Delivery Table
class DeliveryTable:
    def __init__(self):
        self.table = {}  # {peer_port: probability}

    def update_probability(self, peer, prob):
        self.table[peer] = prob

    def get_best_candidates(self, threshold):
        return [peer for peer, prob in self.table.items() if prob >= threshold]

# ---------------------------
# INIT
BASE_PORT = int(sys.argv[1])
PEER_PORTS = [int(p) for p in sys.argv[2:]]

delivery_table = DeliveryTable()
message_queue = []
seen_messages = set()  # กัน message ซ้ำ

# ---------------------------
# SEND
def send_message(peer_port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))
        s.sendall(message.encode())
        s.close()
        print(f"[NODE {BASE_PORT}] Sent → {peer_port}")
        return True
    except (ConnectionRefusedError, socket.timeout):
        return False

# ---------------------------
# FORWARD LOOP
def forward_loop():
    while True:
        candidates = delivery_table.get_best_candidates(FORWARD_THRESHOLD)
        print(f"[NODE {BASE_PORT}] Candidates: {candidates}")

        for msg in message_queue[:]:
            for peer in candidates:
                if send_message(peer, msg):
                    print(f"[NODE {BASE_PORT}] Forwarded message to {peer}")
                    message_queue.remove(msg)
                    break

        time.sleep(UPDATE_INTERVAL)

# ---------------------------
# SERVER (รับข้อความ)
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, BASE_PORT))
    server.listen()

    print(f"[NODE {BASE_PORT}] Listening...")

    while True:
        conn, addr = server.accept()
        data = conn.recv(BUFFER_SIZE).decode()

        msg_id = data.split("|")[0]

        if msg_id not in seen_messages:
            seen_messages.add(msg_id)
            print(f"[NODE {BASE_PORT}] Received NEW: {data}")
            message_queue.append(data)
        else:
            print(f"[NODE {BASE_PORT}] Duplicate ignored")

        conn.close()

# ---------------------------
# MAIN
if __name__ == "__main__":
    # start threads
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # ตั้ง probability (ลองปรับได้)
    for peer in PEER_PORTS:
        delivery_table.update_probability(peer, 0.6)

    # ส่ง message แรก
    for peer in PEER_PORTS:
        msg = f"{BASE_PORT}:{time.time()}|Hello from node {BASE_PORT}"
        if not send_message(peer, msg):
            print(f"[NODE {BASE_PORT}] Store message for {peer}")
            message_queue.append(msg)

    while True:
        time.sleep(1)