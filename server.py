import logging
import socket
import struct
import sys
from concurrent.futures import ThreadPoolExecutor

from log_message_pb2 import LogMessage

HEADER_TYPE = ">L"  # '>L' -> 4 bytes unsigned long | '>Q' -> 8 bytes
HEADER_SIZE = struct.calcsize(HEADER_TYPE)

SERVER_IP = "0.0.0.0"  # "0.0.0.0" ALL interfaces | '192.168.1.45' for WIFI | '127.0.0.1' only this machine
SERVER_PORT = 15000
SERVER_MAX_CONNECTIONS = 100

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",  # 2026-03-28 14:32:01,234 [ERROR] main - test message
    stream=sys.stdout,
)


def recv_exact_bytes(sock: socket.socket, given_length: int) -> bytes | None:
    """function to receive text from sock connection

    This function waits for each connection to receive text from
    socket by maintaining open connection until it is explicitly
    closed.

    Args:
        sock (socket.socket): socket connection
        given_length (int): length of content to extract and return

    Returns:
        bytes | None: return bytes extracted or None when connection closed
    """
    data = b""
    while len(data) < given_length:  # looping to keep connection open for each message
        chunk = sock.recv(given_length - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def handle_client(conn: socket.socket, address: tuple):
    """function to handle client loggers

    In this function we receive bytes from each connection
    and that is written to logger with extracted info.

    Args:
        conn (socket.socket): client connection
        address (tuple): Address of the client connection
    """
    server_logger = logging.getLogger("server")
    server_logger.log(logging.DEBUG, f"client connected {address}")
    try:
        while True:
            # extract header
            header = recv_exact_bytes(conn, HEADER_SIZE)
            if not header:
                break

            # extract payload
            payload_length = struct.unpack(HEADER_TYPE, header)[0]
            payload = recv_exact_bytes(conn, payload_length)
            if not payload:
                break

            # extract info
            lm = LogMessage()
            lm.ParseFromString(payload)
            log_level = getattr(logging, lm.log_level, logging.INFO)
            client = lm.logger
            mac_id = ":".join([f"{b:02x}" for b in lm.mac])
            message = lm.message

            # build client logger
            client_logger = logging.getLogger(client)
            client_logger.log(log_level, f"[{mac_id}] {message}")

    except Exception as e:
        server_logger.log(logging.ERROR, f"Error handling client: {e}")
    finally:
        conn.close()
        server_logger.log(logging.DEBUG, f"Client connection closed {address}")


def main():
    """main function to run logging server

    Info:
    AF_INET → IPv4 addresses | AF_INET6 → IPv6 addresses | AF_UNIX → file path on same machine
    SOCK_STREAM → stream of bytes = TCP | SOCK_DGRAM → datagrams = UDP

    setsockopt(level, option, value)
        level: SOL_SOCKET → the socket layer| IPPROTO_TCP → TCP layer options | IPPROTO_IP → IP layer options
        option: REUSEADDR = "Address already in use" ← error
        value: 1 = true, 0 = false
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(SERVER_MAX_CONNECTIONS)

    server_logger = logging.getLogger("server")
    server_logger.log(logging.INFO, f"Server started on port {SERVER_PORT}")

    try:
        with ThreadPoolExecutor(max_workers=SERVER_MAX_CONNECTIONS) as executor:
            while True:
                conn, address = server_socket.accept()
                executor.submit(handle_client, conn, address)
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
