# PythonExamples-SocketsCStyle

This repository contains a deliberately **C-style / low-level procedural**
Python TCP sockets example.

The goal is educational: show how the classic socket steps

1. create socket
2. bind / listen / accept on the server
3. connect on the client
4. send and receive bytes
5. close sockets explicitly

look in Python when written in a more manual style. It is intentionally less
idiomatic than typical Python code so it can be compared with both:

- a traditional C sockets example, and
- a more idiomatic Python version in
  https://github.com/kristianmk/PythonExamples-Sockets

## Prerequisites

- Python 3
- Two terminal windows or tabs on the same machine

No third-party dependencies are required.

## Files

- `server.py`
- `client.py`

Both programs use:

- host `127.0.0.1`
- port `55556`
- UTF-8 text
- one length-prefixed message per connection
- a maximum application message size of 1024 bytes

## Important TCP note

TCP is a **byte stream**, not a message protocol. A single `send()` on one side
does **not** guarantee a single matching `recv()` on the other side.

To keep the example simple and correct, this repository uses a small
application-level framing rule:

- each message is UTF-8 text
- each message starts with a 4-byte big-endian length prefix
- code first receives the 4-byte length, then keeps receiving until the full
  payload has arrived
- if the announced payload size is larger than 1024 bytes, the connection is
  rejected
- after one request and one response, the connection is closed

This is still intentionally simple, but it avoids the common beginner mistake
of assuming one `recv()` call always returns one complete message.

## Run the example

Open two terminals in the repository directory.

### Terminal 1: start the server

```bash
python3 server.py
```

Expected output:

```text
Starting TCP server on 127.0.0.1:55556
Listening for connections. Press Ctrl+C to stop.
```

### Terminal 2: run the client

```bash
python3 client.py
```

Expected client output:

```text
Connecting to 127.0.0.1:55556
Connected. Sending: 'Hello from client'
Received: 'Server received: Hello from client'
Client socket closed.
```

Expected additional server output after the client connects:

```text
Accepted connection from 127.0.0.1:<client-port>
Received: 'Hello from client'
Sent: 'Server received: Hello from client'
Closed connection from 127.0.0.1:<client-port>
```

You can run the client multiple times while the server stays running and accepts
each connection in sequence.

Stop the server with `Ctrl+C`.

Expected shutdown output:

```text
Server stopped by user.
Listening socket closed.
```

## Protocol limitations

This is intentionally a small teaching example, so the protocol is limited:

- one request and one response per connection
- length-prefixed UTF-8 text only
- no binary payloads
- no concurrency
- no TLS / encryption
- no authentication

Those limitations keep the example focused on the basic TCP socket lifecycle.

## C-style vs. more idiomatic Python

This repository keeps the code explicit on purpose:

- sockets are created and closed manually
- control flow is spelled out step by step
- send/receive framing is implemented directly
- diagnostics are printed explicitly

A more idiomatic Python example would often hide more of that detail by using
context managers, helper classes, `socket.create_server()`, higher-level
abstractions, or file-like wrappers around sockets.

That more idiomatic style is useful in real applications. This repository keeps
the lower-level style because the teaching goal is to make the socket mechanics
easy to see.
