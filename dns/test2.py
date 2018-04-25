sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 53))

while not self.done:
    data = sock.recv(65565)
    print(data)