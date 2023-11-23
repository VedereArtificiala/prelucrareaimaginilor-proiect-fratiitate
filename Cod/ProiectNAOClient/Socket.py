import socket
import time
import cv2
import numpy as np


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

                # Wait for the image data
                image_data = self.client_socket.recv(640*2 * 480*2 * 3)
                img_array = np.frombuffer(image_data, dtype=np.uint8).reshape((480*2, 640*2, 3))
                print("Image received.")
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
