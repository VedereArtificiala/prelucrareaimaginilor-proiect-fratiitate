from Socket import Socket
import cv2


def main():
    # Adresează serverul și portul la care rulează serverul
    server_host = "localhost"  # Adresa IP a serverului
    server_port = 8888

    # Creează o instanță a clasei Socket
    client = Socket(server_host, server_port)

    # Conectează-te la server
    client.connect_to_server()

    try:
        loop = True
        while loop:
            # client.send_text_message("e 2 to e 4");
            # Trimite o comandă de test către server
            img_array = client.request_image()
            # For example, display the image
            while True:
                cv2.imshow('Processed Image', img_array)
                # Break the loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    loop = False
                    break

    except Exception as e:
        print("Error in client:", str(e))

if __name__ == "__main__":
    main()
