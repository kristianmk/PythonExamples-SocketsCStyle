# Written by K. M. Knausgård 2022-01
#
# Simple TCP sockets example.
#
# Python socket documentation: https://docs.python.org/3/library/socket.html
#
# This example is intentionally procedural and explicit so it resembles a
# lower-level C sockets example more than an idiomatic Python version.

import socket


HOST = "127.0.0.1"
PORT = 55556
BACKLOG = 5
BUFFER_SIZE = 256
MAX_MESSAGE_BYTES = 1024
HEADER_SIZE = 4
ACCEPT_TIMEOUT_SECONDS = 1.0


def recv_exactly(sock, byte_count):
    received_bytes = bytearray()

    while len(received_bytes) < byte_count:
        chunk = sock.recv(min(BUFFER_SIZE, byte_count - len(received_bytes)))
        if not chunk:
            if not received_bytes:
                return None
            raise ConnectionError(
                f"Client closed the connection after {len(received_bytes)} of "
                f"{byte_count} expected bytes."
            )

        received_bytes.extend(chunk)

    return bytes(received_bytes)


def send_framed_text(sock, text):
    encoded_text = text.encode("utf-8")
    if len(encoded_text) > MAX_MESSAGE_BYTES:
        raise ValueError(
            f"Refusing to send {len(encoded_text)} bytes; limit is {MAX_MESSAGE_BYTES} bytes."
        )

    header = len(encoded_text).to_bytes(HEADER_SIZE, byteorder="big")
    sock.sendall(header + encoded_text)


def receive_framed_text(sock):
    header = recv_exactly(sock, HEADER_SIZE)
    if header is None:
        return None

    message_length = int.from_bytes(header, byteorder="big")
    if message_length > MAX_MESSAGE_BYTES:
        raise ValueError(
            f"Received length prefix {message_length}, which exceeds the "
            f"{MAX_MESSAGE_BYTES}-byte limit."
        )

    message_bytes = recv_exactly(sock, message_length)
    if message_bytes is None:
        raise ConnectionError("Client closed the connection before sending the payload.")

    return message_bytes.decode("utf-8")


def handle_client_connection(conn, addr):
    print(f"Accepted connection from {addr[0]}:{addr[1]}")

    try:
        client_text = receive_framed_text(conn)
        if client_text is None:
            print("Client disconnected before sending any data.")
            return

        print(f"Received: {client_text!r}")

        response_text = f"Server received: {client_text}"
        send_framed_text(conn, response_text)
        print(f"Sent: {response_text!r}")

    except (ConnectionError, UnicodeDecodeError, ValueError) as exc:
        print(f"Connection handling error for {addr[0]}:{addr[1]}: {exc}")
    finally:
        conn.close()
        print(f"Closed connection from {addr[0]}:{addr[1]}")


def main():
    listen_socket = None

    try:
        print(f"Starting TCP server on {HOST}:{PORT}")

        # Create a TCP/IPv4 socket explicitly, similar to a C sockets example.
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Allow quick restart after the process exits.
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.settimeout(ACCEPT_TIMEOUT_SECONDS)
        listen_socket.bind((HOST, PORT))
        listen_socket.listen(BACKLOG)

        print("Listening for connections. Press Ctrl+C to stop.")

        while True:
            try:
                conn, addr = listen_socket.accept()
            except socket.timeout:
                continue

            handle_client_connection(conn, addr)

    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except OSError as exc:
        print(f"Server socket error: {exc}")
        raise
    finally:
        if listen_socket is not None:
            listen_socket.close()
            print("Listening socket closed.")


if __name__ == "__main__":
    main()
