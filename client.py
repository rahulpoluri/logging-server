import socket
import struct

from log_message_pb2 import LogMessage

SERVER_IP = "127.0.0.1"
SERVER_PORT = 15000
HEADER_TYPE = ">L"


def send_message(sock, log_level, logger, mac_address, message=None):
    lm = LogMessage()
    lm.log_level = log_level
    lm.logger = logger
    lm.mac = mac_address
    if message:
        lm.message = message
    payload = lm.SerializeToString()
    sock.sendall(struct.pack(HEADER_TYPE, len(payload)) + payload)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((SERVER_IP, SERVER_PORT))
    mac_address = bytes([0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF])

    send_message(sock, "DEBUG", "auth", mac_address, "starting auth")
    send_message(sock, "INFO", "main", mac_address, "connected successfully")
    send_message(sock, "WARNING", "db", mac_address, "slow query detected")
    send_message(sock, "ERROR", "main", mac_address, "connection timeout")
    send_message(
        sock, "INFO", "logger", mac_address
    )  # no message - testing optional field
