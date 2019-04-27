import socket
import time


class Server:

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = 1024
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((server_ip, server_port))
        self.client_address = None
        self.file_name = None

    def process_file(self):
        print("Sending...")
        file_to_send = open(self.file_name, "rb")
        file_bytes = bytearray(file_to_send.read())

        self.UDPServerSocket.sendto(str(len(file_bytes)).encode(), self.client_address)

        start_index = 0
        end_index = self.buffer_size

        while True:
            buffered_bytes = file_bytes[start_index:end_index]

            self.UDPServerSocket.sendto(buffered_bytes, self.client_address)
            time.sleep(0.0001)
            start_index += self.buffer_size
            end_index += self.buffer_size

            if start_index > len(file_bytes):
                print("File was sent!")
                break

    def receive_file_name(self):
        received_bytes = self.UDPServerSocket.recvfrom(self.buffer_size)
        self.client_address = received_bytes[1]
        self.file_name = received_bytes[0].decode()

        print(self.file_name, " was requested to be sent")
        try:
            open(self.file_name, "rb")
        except FileNotFoundError:
            print("File with name ", self.file_name, " does not exist")
            self.file_name = None
            return
        return


if __name__ == "__main__":
    server = Server("127.0.0.1", 20001)
    server.receive_file_name()
    server.process_file()
