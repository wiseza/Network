#node.py
import socket
import threading
import time
import sys

from config import (
    HOST,
    BUFFER_SIZE,
    FORWARD_THRESHOLD,
    UPDATE_INTERVAL,
    REINFORCEMENT,
    INITIAL_PHEROMONE,
)

from pheromone_table import PheromoneTable

BASE_PORT = int(sys.argv[1])
PEER_PORTS = [int(p) for p in sys.argv[2:]]

pheromone_table = PheromoneTable()
message_queue = []


def send_message(peer_port, message):
    # 🚫 กัน message วนลูปกลับ node เดิม
    if f"via {BASE_PORT}" in message:
        return False

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, peer_port))

        new_msg = f"{message} -> via {BASE_PORT}"
        s.sendall(new_msg.encode())
        s.close()

        print(f"[NODE {BASE_PORT}] Sent: {new_msg} to {peer_port}")

        # ✅ reinforce เส้นทางที่สำเร็จ
        pheromone_table.reinforce(peer_port, REINFORCEMENT)
        return True

    except (ConnectionRefusedError, socket.timeout):
        print(f"[NODE {BASE_PORT}] Failed to send to {peer_port}")
        return False


def forward_loop():
    while True:
        pheromone_table.decay()
        pheromone_table.show()

        candidates = pheromone_table.get_best_candidates(FORWARD_THRESHOLD)
        print(f"[NODE {BASE_PORT}] Candidates: {candidates}")

        for msg in message_queue[:]:
            for peer in candidates:
                if send_message(peer, msg):
                    message_queue.remove(msg)
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

        print(f"[NODE {BASE_PORT}] Received: {data}")

        # เก็บ message ไว้ forward ต่อ
        message_queue.append(data)

        conn.close()


if __name__ == "__main__":
    # start threads
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=forward_loop, daemon=True).start()

    # 🐜 เริ่มต้น pheromone ให้เพื่อนบ้าน
    for peer in PEER_PORTS:
        pheromone_table.reinforce(peer, INITIAL_PHEROMONE)

    # 🚀 ส่ง message ครั้งแรก
    for peer in PEER_PORTS:
        msg = f"Hello from node {BASE_PORT}"
        if not send_message(peer, msg):
            message_queue.append(msg)

    while True:
        time.sleep(1)