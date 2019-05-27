"""
UDP Server-Client assignment

Server program

Authors:
    Timur Uzakov ( uzakoti1 )
    Nikita Dvoriadkin ( dvorinik )
"""

import socket
import zlib
import hashlib
import time


def md5(filename):
    m = hashlib.md5()
    for line in open(filename, 'rb'):
        m.update(line)
    return m.hexdigest()


def crc(bytes):
    c = zlib.crc32(bytes, 0xFFFF)
    return c


class Server:

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = 1024
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((server_ip, server_port))
        self.client_address = None
        self.file_name = None
        self.error_packets = []
        self.count_packets = 10  # N packets

    def process_file(self):
        start_time = time.time()
        md5_check = ""
        file_bytes = []
        while True:
            print("Sending...")

            if md5_check != "Error":
                file_to_send = open(self.file_name, "rb")
                file_bytes = bytearray(file_to_send.read())
                self.UDPServerSocket.sendto(str(len(file_bytes)).encode(), self.client_address)

            start_index = 0
            end_index = self.buffer_size
            n = 0
            while True:

                if n < self.count_packets:

                    buffered_bytes = file_bytes[start_index:end_index]
                    self.UDPServerSocket.sendto(buffered_bytes, self.client_address)

                    crc_server = str(crc(buffered_bytes)).encode()
                    self.UDPServerSocket.sendto(crc_server, self.client_address)

                    start_index += self.buffer_size
                    end_index += self.buffer_size
                    n += 1

                    if start_index > len(file_bytes):
                        break

                else:
                    c = 0
                    while True:
                        crc_check_data = self.UDPServerSocket.recvfrom(self.buffer_size)
                        crc_check = crc_check_data[0].decode()
                        if crc_check == "Done":
                            break
                        self.error_packets.append(int(crc_check))
                        c += 1

                    while self.error_packets:
                        start_error_index = self.error_packets.pop(0) * self.buffer_size
                        end_error_index = start_error_index + self.buffer_size

                        buffered_bytes = file_bytes[start_error_index:end_error_index]
                        self.UDPServerSocket.sendto(buffered_bytes, self.client_address)

                    n = 0

            md5_server = str(md5(self.file_name)).encode()
            self.UDPServerSocket.sendto(md5_server, self.client_address)
            md5_check_data = self.UDPServerSocket.recvfrom(self.buffer_size)
            md5_check = md5_check_data[0].decode()
            if md5_check == "FILE OK":
                print("File was sent!")
                print("Total time: ", time.time()-start_time, " sec")
                break
            else:
                print("MD5 check error, receive again..")

    def receive_file_name(self):
        received_bytes = self.UDPServerSocket.recvfrom(self.buffer_size)
        self.client_address = received_bytes[1]
        self.file_name = received_bytes[0].decode()

        print(self.file_name, " was requested to be sent")
        try:
            open(self.file_name, "rb")
            check_file_name = "OK"
            filename_data = str(check_file_name).encode()
            self.UDPServerSocket.sendto(filename_data, self.client_address)
        except FileNotFoundError:
            print("File with name ", self.file_name, " does not exist")
            self.file_name = None
            check_file_name = "Error"
            filename_data = str(check_file_name).encode()
            self.UDPServerSocket.sendto(filename_data, self.client_address)
            return 404
        return


if __name__ == "__main__":

    server = Server("127.0.0.1", 20001)  # localhost

    # server = Server("147.32.216.212", 20001) # write server's IP address

    print("Waiting for client request...")
    if server.receive_file_name() != 404:
        server.process_file()
