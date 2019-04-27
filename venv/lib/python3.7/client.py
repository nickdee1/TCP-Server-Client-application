import socket


class Client:

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = 1024
        self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.file_name = None
        self.file_size = None

    def send_file_download_request(self, filename):
        print("Sending request to the server...")
        self.file_name = filename
        filename_data = str(filename).encode()

        self.UDPClientSocket.sendto(filename_data, (self.server_ip, self.server_port))

        self.file_size = self.UDPClientSocket.recvfrom(1024)
        self.file_size = int(self.file_size[0].decode())

    def receive_file(self, with_name):
        print("Receiving file...")
        received_file_size = 0
        output_file = open(with_name, "ab")

        while True:
            received_bytes = self.UDPClientSocket.recvfrom(self.buffer_size)
            output_file.write(received_bytes[0])
            received_file_size += 1024

            if received_file_size > self.file_size:
                print("File was received and saved as ", with_name)
                break


if __name__ == "__main__":
    client = Client("127.0.0.1", 20001)
    client.send_file_download_request("10mb.jpg")
    client.receive_file(with_name="new_file.jpg")