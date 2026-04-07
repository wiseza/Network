import socket
import threading
import sys
from config import HOST, BASE_PORT, BUFFER_SIZE

peer_id = int(sys.argv[1])
PORT = BASE_PORT + peer_id

# ---------------------------
# Listener (รับข้อความ)
def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)

    print(f"\n[PEER {peer_id}] Listening on {PORT}\n", flush=True)

    while True:
        conn, addr = sock.accept()
        data = conn.recv(BUFFER_SIZE)

        # 👇 เว้นบรรทัด + รีพิมพ์ prompt ใหม่
        print(f"\n[PEER {peer_id}] From {addr}: {data.decode()}")
        print("Send to peer ID: ", end="", flush=True)

        conn.close()

# ---------------------------
# Sender (ส่งข้อความ)
def send_message(target_peer_id, message):
    target_port = BASE_PORT + target_peer_id
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, target_port))
        sock.sendall(message.encode())
        print(f"[PEER {peer_id}] Sent to {target_peer_id}: {message}")
    except ConnectionRefusedError:
        print(f"[PEER {peer_id}] Peer {target_peer_id} not online")
    finally:
        sock.close()

# ---------------------------
# Start listener thread
threading.Thread(target=listen, daemon=True).start()

# ---------------------------
# Main loop (ส่งข้อความ)
while True:
    try:
        target = int(input("Send to peer ID: "))
        msg = input("Message: ")
        send_message(target, msg)
    except ValueError:
        print("[PEER] กรุณาใส่ตัวเลขนะ 😅")