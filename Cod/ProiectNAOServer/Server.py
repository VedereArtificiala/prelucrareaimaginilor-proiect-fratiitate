# -*- coding: utf-8 -*-

import socket
from naoqi import *
import vision_definitions

def connect_to_robot(robot_ip, robot_port):
    # Initialize proxies for motion, posture, video, and audio
    motion_proxy = ALProxy("ALMotion", robot_ip, robot_port)
    posture_proxy = ALProxy("ALRobotPosture", robot_ip, robot_port)
    camProxy = ""
    camProxy = ALProxy("ALVideoDevice", robot_ip, robot_port)
    audio_proxy = ALProxy("ALTextToSpeech", robot_ip, robot_port)

    # Set initial robot posture and head position
    posture_proxy.goToPosture("StandInit", 0.1)
    motion_proxy.setAngles("HeadYaw", 0.0, 0.1)
    motion_proxy.setAngles("HeadPitch", 0.4, 0.1)

    return motion_proxy, posture_proxy, camProxy, audio_proxy


def take_photo(robot_ip, robot_port, output_folder='output'):
    # Connect to the robot
    try:
        video_device = ALProxy("ALVideoDevice", robot_ip, robot_port)
    except Exception as e:
        print("Error connecting to the robot:", str(e))
        return

    # Make sure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create a video module
    video_client = video_device.subscribeCamera("photo_client", 1, 3, 13, 5)

    # Capture a photo
    image_data = video_device.getImageRemote(video_client)
    video_device.unsubscribe(video_client)

    # Extract the image data
    width, height, channels, image_bytes = image_data[0], image_data[1], image_data[2], image_data[6]

    return width, height, channels, image_bytes
def say_text(audio_proxy, text):
    # Use ALTextToSpeech to make the robot say the provided text
    audio_proxy.say(text)

def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print("Server listening on {}:{}".format(host, port))
    return server_socket


def main():
    robot_ip = "192.168.1.100"  # Replace with your robot's IP address
    robot_port = 9559
    server_host = "0.0.0.0"  # Listen on all available interfaces
    server_port = 8888

    motion_proxy, posture_proxy, camProxy, audio_proxy = connect_to_robot(robot_ip, robot_port)
    if motion_proxy is None:
        return

    server_socket = start_server(server_host, server_port)

    try:
        while True:
            print("Waiting for a connection...")
            client_socket, client_address = server_socket.accept()
            print("Connection established with:", client_address)

            while True:
                # Wait for a request from the client
                request = client_socket.recv(1024).decode()

                if not request:
                    break  # Break the loop if the client disconnects

                # Handle different types of requests
                if request == "REQUEST_IMAGE":
                    # Send the image data to the client
                    width, height, channels, image_bytes = take_photo(robot_ip, robot_port)
                    # Send the image data over the socket

                    client_socket.send(image_bytes)

                elif request.startswith("SPEAK:"):
                    # Extract the message from the request
                    message = request[len("SPEAK:"):]
                    print(message)
                    # Process the message (e.g., use TextToSpeech)
                    say_text(audio_proxy, str(message))

                    # Send a response back to the client (optional)
                    print("Message received and processed.")

    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        # Close the server socket
        server_socket.close()


if __name__ == "__main__":
    main()
