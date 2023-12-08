# -*- coding: utf-8 -*-

import socket
from naoqi import *
import cv2
import struct
import vision_definitions

online = False  # cu sau fara robot


class Server:
    def __init__(self):
        # initializare server
        self.img = 1
        self.robot_ip = "192.168.1.100"
        self.robot_port = 9559
        self.server_host = "0.0.0.0"
        self.server_port = 8888
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(1)

        if online:
            # initializare proxy-uri

            self.motion_proxy = ALProxy("ALMotion", self.robot_ip, self.robot_port)
            self.posture_proxy = ALProxy("ALRobotPosture", self.robot_ip, self.robot_port)
            self.video_proxy = ALProxy("ALVideoDevice", self.robot_ip, self.robot_port)
            self.audio_proxy = ALProxy("ALTextToSpeech", self.robot_ip, self.robot_port)

            # initializare postura

            self.posture_proxy.goToPosture("StandInit", 0.1)
            self.motion_proxy.setAngles("HeadYaw", 0.0, 0.1)
            self.motion_proxy.setAngles("HeadPitch", 0.4, 0.1)

            # initializare camera

            self.video_client = self.video_proxy.subscribeCamera("photo_client", 1, 3, 13, 5)

    def take_photo(self):
        try:
            if online:
                image_data = self.video_proxy.getImageRemote(self.video_client)
                width, height, channels, image_bytes = image_data[0], image_data[1], image_data[2], image_data[6]
                return width, height, channels, image_bytes
            elif not online:
                image = cv2.imread("Output/dataset"+str(self.img)+".png")

                self.img += 1
                return image
        except Exception as e:
            print("Error connecting to the robot:", str(e))
            return

    def say_text(self, text):
        if online:
            # Use ALTextToSpeech to make the robot say the provided text
            self.audio_proxy.say(text)
        elif not online:
            print(text)

    def main(self):

        try:
            while True:
                print("Waiting for a connection...")
                self.img = 1
                client_socket, client_address = self.server_socket.accept()
                print("Connection established with:", client_address)

                while True:
                    # Wait for a request from the client
                    request = client_socket.recv(1024).decode()

                    if not request:
                        break  # Break the loop if the client disconnects

                    # Handle different types of requests
                    if request == "REQUEST_IMAGE":
                        if online:
                            # Send the image data to the client
                            width, height, channels, image_bytes = self.take_photo()
                            # Send the image data over the socket

                            client_socket.send(image_bytes)
                        elif not online:
                            image = self.take_photo()
                            image_bytes = cv2.imencode('.png', image)[1].tobytes()

                            # Trimite dimensiunile imaginii la client
                            client_socket.sendall(struct.pack("!Q", len(image_bytes)))

                            # Trimite datele imaginii la client
                            client_socket.sendall(image_bytes)

                    elif request.startswith("SPEAK:"):
                        # Extract the message from the request
                        message = request[len("SPEAK:"):]
                        print(message)
                        # Process the message (e.g., use TextToSpeech)
                        self.say_text(str(message))
                        # Send a response back to the client (optional)
                        print("Message received and processed.")


        except KeyboardInterrupt:
            print("\nServer shutting down.")
        finally:
            # Close the server socket
            print("Disconnecting...")
            self.server_socket.close()
            if online:
                self.video_proxy.unsubscribe(self.video_client)


def main():
    server = Server()
    server.main()


main()
