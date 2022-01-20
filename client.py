# Written by K. M. Knausgård 2022-01
#
# Python socket documentation: https://docs.python.org/3/library/socket.html
#
# This example purposely created very similar to the C-example here:
# Better Python version here:

import socket


HOST = "127.0.0.1"  # localhost
PORT = 55556


def main():
    # Create socket for address family IPv4 (AF_INET), type stream (almost always means TCP).
    # Alternative address families could be AF_INET6 for IPv6, AF_BTH for bluetooth and more..
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to server (block until accepted)
    s.connect((HOST, PORT))

    # Send encoded data
    s.send(b"Hello world")

    # Receive response
    data = s.recv(1024)

    # Print result
    print(data.decode())

    # Close connection
    s.close()


if __name__ == '__main__':
    main()

