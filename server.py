# Written by K. M. Knausgård 2022-01
#
# Simple TCP sockets example.
#
# Python socket documentation: https://docs.python.org/3/library/socket.html
#
# This example is intentionally procedural and explicit so it resembles a
# lower-level C sockets example more than an idiomatic Python version.

import errno
import socket


HOST = "127.0.0.1"
PORT = 55556
BACKLOG = 5
BUFFER_SIZE = 256
MAX_MESSAGE_BYTES = 1024


def send_text_line(sock, text):
    encoded_text = text.encode("utf-8")
    if len(encoded_text) > MAX_MESSAGE_BYTES:
        raise ValueError(
            f"Refusing to send {len(encoded_text)} bytes; limit is {MAX_MESSAGE_BYTES} bytes."
        )

    sock.sendall(encoded_text + b"\n")


def receive_text_line(sock):
    received_bytes = bytearray()

    while True:
        chunk = sock.recv(BUFFER_SIZE)
        if not chunk:
            if not received_bytes:
                return None
            raise ConnectionError(
                "Client closed the connection before sending a newline-terminated message."
            )

        received_bytes.extend(chunk)
        if len(received_bytes) > MAX_MESSAGE_BYTES:
            raise ValueError(
                f"Received more than {MAX_MESSAGE_BYTES} bytes before a newline."
            )

        newline_index = received_bytes.find(b"\n")
        if newline_index != -1:
            message_bytes = bytes(received_bytes[:newline_index])
            trailing_bytes = bytes(received_bytes[newline_index + 1 :])
            return message_bytes.decode("utf-8"), trailing_bytes


def handle_client_connection(conn, addr):
    print(f"Accepted connection from {addr[0]}:{addr[1]}")

    try:
        received_message = receive_text_line(conn)
        if received_message is None:
            print("Client disconnected before sending any data.")
            return

        client_text, trailing_bytes = received_message
        if trailing_bytes:
            print(
                "Ignoring trailing bytes buffered after the first request because "
                "this example handles one request per connection."
            )

        print(f"Received: {client_text!r}")

        response_text = f"Server received: {client_text}"
        send_text_line(conn, response_text)
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
        listen_socket.bind((HOST, PORT))
        listen_socket.listen(BACKLOG)

        print("Listening for connections. Press Ctrl+C to stop.")

        while True:
            try:
                conn, addr = listen_socket.accept()
            except OSError as exc:
                if exc.errno == errno.EINTR:
                    print("\nServer stopped by user.")
                    break
                raise

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
