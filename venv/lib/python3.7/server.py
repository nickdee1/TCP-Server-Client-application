import socket


class Server:

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = 1024
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((server_ip, server_port))

    # TODO: - implement reading and sending file methods
    def process_file(self, file_name):
        byte_array = None
        with open(file_name, "rb") as input_file:
            file_bytes = input_file.read()
            byte_array = bytearray(file_bytes)