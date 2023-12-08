import socket
import struct
import time
import cv2
import numpy as np

online = False # cu sau fara robot

class Socket:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = None

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_host, self.server_port))
            print("Connected to the server.")
        except Exception as e:
            print("Error connecting to the server:", str(e))

    def request_image(self):
        try:
            if self.client_socket:
                self.client_socket.send("REQUEST_IMAGE".encode())
                print("Image request sent.")

                if online:
                    # Wait for the image data
                    image_data = self.client_socket.recv(640*2 * 480*2 * 3)
                    img_array = np.frombuffer(image_data, dtype=np.uint8).reshape((480*2, 640*2, 3))
                    print("Image received.")
                    return img_array
                elif not online:
                    image_size_data = self.client_socket.recv(8)
                    image_size = struct.unpack("!Q", image_size_data)[0]
                    image_data = b''

                    while len(image_data) < image_size:
                        chunk = self.client_socket.recv(min(image_size - len(image_data), 4096))
                        if chunk == b'':
                            raise RuntimeError("Socket connection broken")
                        image_data += chunk

                    print("Received image data size:", len(image_data))

                    # Transforma datele intr-un array numpy
                    img_array = np.frombuffer(image_data, dtype=np.uint8)#.reshape((480*2, 640*2, 3))
                    img_array = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    return img_array
            else:
                print("Not connected to the server. Call connect_to_server() first.")
        except Exception as e:
            print("Error receiving image:", str(e))
            return None

    def send_text_message(self, message):
        try:
            if self.client_socket:
                self.client_socket.send(("SPEAK:" + message).encode())
                print("Text message sent:", message)
            else:
                print("Not connected to the server. Call connect_to_server() first.")
        except Exception as e:
            print("Error sending text message:", str(e))

    def close_connection(self):
        try:
            if self.client_socket:
                self.client_socket.close()
                print("Connection closed.")
            else:
                print("Not connected to the server.")
        except Exception as e:
            print("Error closing connection:", str(e))
