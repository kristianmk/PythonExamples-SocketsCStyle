# Written by K. M. Knausgård 2022-01
#
# Python socket documentation: https://docs.python.org/3/library/socket.html
#
# This example is intentionally procedural and explicit so it resembles a
# lower-level C sockets example more than an idiomatic Python version.

import socket


HOST = "127.0.0.1"
PORT = 55556
BUFFER_SIZE = 256
MAX_MESSAGE_BYTES = 1024
CLIENT_MESSAGE = "Hello from client"


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
                "Server closed the connection before sending a newline-terminated message."
            )

        received_bytes.extend(chunk)
        if len(received_bytes) > MAX_MESSAGE_BYTES:
            raise ValueError(
                f"Received more than {MAX_MESSAGE_BYTES} bytes before a newline."
            )

        newline_index = received_bytes.find(b"\n")
        if newline_index != -1:
            if newline_index + 1 != len(received_bytes):
                raise ValueError(
                    "Received extra bytes after the first newline. "
                    "This example supports one text line per connection."
                )

            message_bytes = bytes(received_bytes[:newline_index])
            return message_bytes.decode("utf-8")


def main():
    client_socket = None

    try:
        print(f"Connecting to {HOST}:{PORT}")

        # Create a TCP/IPv4 socket explicitly, similar to a C sockets example.
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the listening server socket.
        client_socket.connect((HOST, PORT))
        print(f"Connected. Sending: {CLIENT_MESSAGE!r}")

        # TCP is a byte stream, so this example adds a newline to mark where
        # the application-level message ends.
        send_text_line(client_socket, CLIENT_MESSAGE)

        response_text = receive_text_line(client_socket)
        if response_text is None:
            raise ConnectionError("Server closed the connection without sending a reply.")

        print(f"Received: {response_text!r}")

    except (ConnectionError, OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"Client error: {exc}")
        raise
    finally:
        if client_socket is not None:
            client_socket.close()
            print("Client socket closed.")


if __name__ == "__main__":
    main()
