# logging-server

This is logging server created to listen to client loggers over TCP connection using protobuf format

This server is expected to run continuously listening to new client connections(max up to 100 clients)
and try to get the length prefixed messages using protobuf format.

This server is written in python and uses Threadpooling instead of async.

### Requirements 
- Language used: Python==3.8+
- Internal Libraries used: logging, socket, struct, sys, ThreadPoolExecutor
- External Libraries used: protobuf==7.34.1

### How to install in Mac
- Install python3
- Install git
- Clone the repository and cd into repository
- Run `python3 -m venv .venv`
- Run `source .venv/bin/activate`
- Run `pip install -r requirements.txt`

### How to run
- Run `python3 server.py`
- In a different terminal run `python3 client.py`
- Check terminal with server.py for results

### Compiling the .proto file
.proto file is the schema which is utilized by both client and server to 
communicate the structure of the messages sent which can be compiled to language specific schema file.

Here as we are using python so it can be compiled using protobuf library installed on local machine using `brew install protobuf`

To compile .proto file use command: `protoc --python_out=. log_message.proto`

### Design decisions

#### Why ThreadPoolExecutor
ThreadPoolExecutor handles connections automatically pooling them and making more connections
wait in queue until connections are available.

#### Why threading over async
Threading is more safe for I/O bound work as it manages threads completely as separate context, most threads are in waiting state blocked by sock.recv() which releases GIL for thread switching freely

#### Why recv_exact_bytes
To support partial read as information might come in various network packets with interruptions.

#### Why use SO_REUSEADDR
This flag is used so that address can be reused by the server when it restarts abruptly. In general OS remembers port for few secs and we get error to avoid it and not raise error "already in use" this flag is needed.

#### Protocol buffers
`[ 4 bytes: length ][ N bytes: protobuf payload ]`
As per given client connection info each message is length prefixed
for prefix ">L" is used "L" which depicts unsigned long has 4 bytes which means it can support up to 2^32 bytes ~4GB.

">" Big-endian(most significant byte first) indicates network byte order.

We have used struct library to pack and unpack content length with this symbols.