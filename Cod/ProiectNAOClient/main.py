from Socket import Socket
from Board import Board
import cv2


def main():
    # Adresează serverul și portul la care rulează serverul
    server_host = "localhost"  # Adresa IP a serverului
    server_port = 8888

    # Creează o instanță a clasei Socket
    client = Socket(server_host, server_port)

    # Conectează-te la server
    client.connect_to_server()

    # Preia imaginea initiala cu tabla
    img_array = client.request_image()

    # Creeaza o instanta a clasei Board

    board = Board(img_array)

    try:
        loop = True
        while loop:
            a = cv2.waitKey(1)
            if a & 0xFF == ord('q'):
                loop = False
            if a & 0xFF == ord(' '):
                player_color = board.get_turn()
                move = board.get_next_move(client.request_image())
                client.send_move_message(player_color, move)
    except Exception as e:
        print("Error in client:", str(e))


if __name__ == "__main__":
    main()
