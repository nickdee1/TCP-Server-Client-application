"""
UDP Server-Client assignment

Client program

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


class Client:

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = 1024
        self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.file_name = None
        self.file_size = None
        self.max_speed = 1024   # KB/s
        self.error_packets = []
        self.count_packets = 10  # N packets

    def send_file_download_request(self, filename):
        print("Sending request to the server...")
        self.file_name = filename
        filename_data = str(filename).encode()

        self.UDPClientSocket.sendto(filename_data, (self.server_ip, self.server_port))
        received_bytes = self.UDPClientSocket.recvfrom(self.buffer_size)
        check_file_name = received_bytes[0].decode()

        if check_file_name == "OK":
            self.file_size = self.UDPClientSocket.recvfrom(self.buffer_size)
            self.file_size = int(self.file_size[0].decode())
        else:
            return 404

    def receive_file(self, name_of_file):
        start_time = time.time()
        timer = start_time
        time.sleep(0.1)
        while True:

            print("Receiving file...", end="")
            received_file_size = 0
            output_file = open(name_of_file, "wb")
            saved_bytes = bytearray()
            all_received_bytes = 0
            i = 0  # packet count
            n = 0
            start_index = 0
            end_index = self.buffer_size

            while True:

                if n < self.count_packets:

                    received_bytes = self.UDPClientSocket.recvfrom(self.buffer_size)

                    crc_server_data = self.UDPClientSocket.recvfrom(self.buffer_size)
                    crc_server = crc_server_data[0].decode()
                    crc_client = crc(received_bytes[0])

                    all_received_bytes += len(received_bytes[0])
                    now_speed = all_received_bytes / (time.time() - start_time) / self.buffer_size
                    if now_speed > self.max_speed:
                        while True:
                            now_speed = all_received_bytes / (time.time() - start_time) / self.buffer_size
                            if now_speed < self.max_speed:
                                break

                    if int(crc_client) == int(crc_server):
                        received_file_size += self.buffer_size
                        saved_bytes[start_index:end_index] = received_bytes[0]
                    else:
                        self.error_packets.append(i)
                        for j in range(start_index, end_index):
                            saved_bytes += b'0'

                    i += 1
                    n += 1

                    start_index += self.buffer_size
                    end_index += self.buffer_size

                    if (time.time() - timer) >= 1.0:
                        timer = time.time()
                        print(".", end="")

                    if received_file_size > self.file_size:
                        output_file.write(saved_bytes)
                        output_file.close()
                        # print("Total speed: ", all_received_bytes / (time.time() - start_time) / 1024, " KB/s\n")
                        break
                else:
                    c = 0
                    while c < self.count_packets:
                        try:
                            crc_check_data = str(self.error_packets[c]).encode()
                            self.UDPClientSocket.sendto(crc_check_data, (self.server_ip, self.server_port))
                            c += 1
                        except IndexError:
                            crc_check_data = str("Done").encode()
                            self.UDPClientSocket.sendto(crc_check_data, (self.server_ip, self.server_port))
                            break

                    while self.error_packets:
                        start_error_index = self.error_packets.pop(0) * self.buffer_size
                        end_error_index = start_error_index + self.buffer_size
                        received_bytes = self.UDPClientSocket.recvfrom(self.buffer_size)
                        saved_bytes[start_error_index:end_error_index] = received_bytes[0]
                        received_file_size += self.buffer_size

                        all_received_bytes += len(received_bytes[0])
                        now_speed = all_received_bytes / (time.time() - start_time) / self.buffer_size
                        if now_speed > self.max_speed:
                            while True:
                                now_speed = all_received_bytes / (time.time() - start_time) / self.buffer_size
                                if now_speed < self.max_speed:
                                    break

                    n = 0

            md5_server_data = self.UDPClientSocket.recvfrom(self.buffer_size)
            md5_server = md5_server_data[0].decode()
            md5_client = md5(name_of_file)

            if md5_server == md5_client:
                md5_check = "FILE OK"
                md5_check_data = str(md5_check).encode()
                self.UDPClientSocket.sendto(md5_check_data, (self.server_ip, self.server_port))
                print("\nTotal time: ", time.time() - start_time, " sec")
                print("Total size: ", received_file_size/1024, " kB")
                print("File was received and saved as ", name_of_file)
                break
            else:
                md5_check = "Error"
                md5_check_data = str(md5_check).encode()
                self.UDPClientSocket.sendto(md5_check_data, (self.server_ip, self.server_port))
                print("Error md5")


if __name__ == "__main__":

    client = Client("127.0.0.1", 20001)  # localhost

    # client = Client("147.32.219.238", 20001) # write server's IP address

    print("Enter name of file: ")
    file_name = input()
    if client.send_file_download_request(file_name) != 404:
        client.receive_file(name_of_file=file_name)
    else:
        print("File with name ", file_name, " does not exist")
