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
HEADER_SIZE = 4
CLIENT_MESSAGE = "Hello from client"


def recv_exactly(sock, byte_count):
    received_bytes = bytearray()

    while len(received_bytes) < byte_count:
        chunk = sock.recv(min(BUFFER_SIZE, byte_count - len(received_bytes)))
        if not chunk:
            if not received_bytes:
                return None
            raise ConnectionError(
                f"Server closed the connection after {len(received_bytes)} of "
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
        raise ConnectionError("Server closed the connection before sending the payload.")

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

        # TCP is a byte stream, so this example sends a fixed-size length
        # prefix before the UTF-8 payload.
        send_framed_text(client_socket, CLIENT_MESSAGE)

        response_text = receive_framed_text(client_socket)
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
