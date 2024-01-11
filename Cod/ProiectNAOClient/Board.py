import chess
import cv2
import numpy as np
from utility import intersections, extend_line, average_line, get_points, intersection, sort_points, to_center
from Chess import Chess

director = 'images/'
imag = cv2.imread(director + 'img.png')
test_img = cv2.imread(director + 'img_1.png')
img_init = cv2.imread(director + 'init.png')
img_init2 = cv2.imread(director + 'init2.png')
img_start = cv2.imread(director + 'start.png')
img_start2 = cv2.imread(director + 'start2.png')
image1 = cv2.imread(director + 'move1.png')
image1_2 = cv2.imread(director + 'move1_2.png')
image2 = cv2.imread(director + 'move2.png')
image3 = cv2.imread(director + 'move3.png')
image4 = cv2.imread(director + 'move4.png')
img_ill_1 = cv2.imread(director + 'illegal_move1.png')
img_ill_2 = cv2.imread(director + 'illegal_move2.png')

debug = True
stretch = False


class Board:

    def __init__(self, img, down_scale=2):
        self.game = Chess()
        self.counter = 0
        self.previous_img = None
        self.board = None
        self.trapez = None
        self.trapezf32 = None
        self.width = img.shape[1] // down_scale
        self.height = img.shape[0] // down_scale
        self.current_img = cv2.resize(img, (self.width, self.height))
        self.current_img = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2GRAY)

        self.horizontal_lines = None
        self.vertical_lines = None
        self.corners = None
        self.oldgrid = np.zeros((8, 8), dtype=int)
        self.grid = np.zeros((8, 8), dtype=int)
        self.difgrid = np.zeros((8, 8), dtype=int)

        cv2.imshow('Image Grayscale', self.current_img)
        # cv2.waitKey(0)
        # get_points("Img", self.current_img)

        # Cropare tabla
        self.get_board_contour()
        self.stretch = np.array([
            (self.width, 0),
            (0, 0),
            (0, self.height),
            (self.width, self.height)
        ], dtype=np.float32)

        self.stretch_board()
        self.get_lines()
        self.get_grid()

    def show_grid(self):
        img_lines = np.copy(self.current_img) * 0
        for i in range(0, 9):
            for j in range(0, 2):
                cv2.circle(img_lines, self.vertical_lines[j][i], 8, (255, 255, 255), -1)
                cv2.circle(img_lines, self.horizontal_lines[j][i], 8, (255, 255, 255), -1)
            cv2.line(img_lines, self.vertical_lines[0][i], self.vertical_lines[1][i], (255, 255, 255), 2)
            cv2.line(img_lines, self.horizontal_lines[0][i], self.horizontal_lines[1][i], (255, 255, 255), 2)
        grid = cv2.addWeighted(self.current_img, 0.8, img_lines, 1, 0)
        cv2.imshow('Grid edges', grid)

    def get_next_move(self, img):
        self.counter = self.counter + 1
        self.previous_img = self.current_img
        self.oldgrid=np.copy(self.grid)
        self.current_img = cv2.resize(img, (self.width, self.height))
        self.current_img = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2GRAY)
        self.current_img = self.current_img * self.board
        self.stretch_board()
        self.show_grid()
        self.get_grid()
        mutare = self.validate_move()

        if debug:
            cv2.imshow('Current Image', self.current_img)
            cv2.imshow('Previous Image', self.previous_img)

        if mutare is not None:
            return mutare
        elif self.counter > 1:
            return "No move was made!"
        else:
            return "The match can begin!"

    def validate_move(self):
        move1 = 0
        move2 = 0
        move3 = 0
        move4 = 0
        mutari = 0
        for i in range(0, 8):
            for j in range(0, 8):
                if (self.difgrid[i][j] > np.mean(self.difgrid) * 4):
                    mutari = mutari + 1
        if(self.counter>1):
            threshold = np.mean(self.difgrid) * 4
            if(mutari == 2):
                print(self.counter)
                for i in range(0,8):
                    for j in range (0,8):
                        if(self.difgrid[i][j]>threshold):
                            if move1==0:
                                move1 = chr(ord('a') + i)+str(j+1)
                                print(move1)
                            else:
                                move2 = chr(ord('a') + i) + str(j+1)
                                print(move2)
                                #trimit mutarile la chess engine pentru validare
                                valid = None
                                valid, mesaj = self.game.make_move(move1+move2)
                                if(valid == False):
                                    valid, mesaj = self.game.make_move(move2+move1)
                                    if(valid == False):
                                        return "Invalid move: "+move1+" to "+move2
                                    else:
                                        if (mesaj == "Check"):
                                            return move2+" to "+move1+" Check!"
                                        else:
                                            return move2 + " to " + move1
                                else:
                                    if (mesaj == "Check Mate"):
                                        return " Won!"
                                    else:
                                        return move1+" to "+move2
            elif (mutari == 4):
                print(self.counter)
                if (self.difgrid[7][0] > threshold)\
                        and (self.difgrid[6][0] > threshold)\
                        and (self.difgrid[5][0] > threshold)\
                        and (self.difgrid[4][0] > threshold):
                    print("rocada mica alb")
                    valid, mesaj = self.game.make_move("e1g1")
                    if valid:
                        return "Kingside Castling. e1 to g1"
                if (self.difgrid[0][0] > threshold)\
                    and (self.difgrid[2][0] > threshold) \
                    and (self.difgrid[3][0] > threshold) \
                    and (self.difgrid[4][0] > threshold):
                    print("rocada mare alb")
                    valid, mesaj = self.game.make_move("e1c1")
                    if valid:
                        return "Queenside Castling. e1 to c1"
                if (self.difgrid[7][7] > threshold)\
                        and (self.difgrid[6][7] > threshold)\
                        and (self.difgrid[5][7] > threshold)\
                        and (self.difgrid[4][7] > threshold):
                    print("rocada mica negru")
                    valid, mesaj = self.game.make_move("e8g8")
                    if valid:
                        return "Kingside Castling. e8 to g8"
                if (self.difgrid[0][7] > threshold)\
                    and (self.difgrid[2][7] > threshold) \
                    and (self.difgrid[3][7] > threshold) \
                    and (self.difgrid[4][7] > threshold):
                    print("rocada mare negru")
                    valid, mesaj = self.game.make_move("e8c8")
                    if valid:
                        return "Queenside Castling. e8 to c8"
        else:
            pass

    def get_turn(self):
        if(self.counter >= 1):
            return "black" if self.game.board.turn == chess.BLACK else "white"
        else:
            return ""

    def get_board_contour(self):
        self.board = np.zeros((self.height, self.width), dtype=np.uint8)

        frame = self.current_img
        edges = cv2.Canny(frame, 100, 150, apertureSize=3)
        # get_points('Egdes', edges)
        # cv2.imshow('Edges', edges)

        rho = 1  # distance resolution in pixels of the Hough grid
        theta = np.pi / 180  # angular resolution in radians of the Hough grid
        threshold = 60  # minimum number of votes (intersections in Hough grid cell)
        min_line_length = 400  # minimum number of pixels making up a line
        max_line_gap = 4  # maximum gap in pixels between connectable line segments

        img_lines = np.copy(edges)
        corners = []
        lines = cv2.HoughLinesP(edges, rho, theta, threshold, None, min_line_length, max_line_gap)
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # print(f'{line[0]}')
            if abs(y1-y2) > 10:
                corners.append((x1, y1))
                corners.append((x2, y2))
                cv2.line(img_lines, (x1, y1), (x2, y2), (255, 255, 255), 2)

        corners = sort_points(corners, (self.width // 2, self.height // 2))
        center = intersection(corners[0] + corners[2], corners[1] + corners[3])
        corners = to_center(corners, center, 0.04)

        for (x1, y1) in corners:
            cv2.circle(img_lines, (x1, y1), 3, (255, 50, 255), -1)

        upper_right = (516, 50)  # (466, 138)  # (516, 50)  # (478, 131)
        upper_left = (140, 54)  # (191, 136)  # (140, 54)  # (178, 128)
        lower_left = (84, 451)  # (164, 420)  # (84, 451)  # (150, 430)
        lower_right = (578, 451)  # (493, 426)  # (578, 451)  # (508, 434)

        self.trapez = np.array([
            upper_right,
            upper_left,
            lower_left,
            lower_right
        ], dtype=np.int32)

        self.trapez = np.array(corners, dtype=np.int32)

        cv2.fillConvexPoly(self.board, self.trapez, 1)
        # cv2.imshow('Trapezoid', self.board * 255)
        self.current_img = self.current_img * self.board
        cv2.imshow('Trapezoid', img_lines)

    def get_current_image(self):
        return self.current_img

    def set_lines(self):
        pass

    def stretch_board(self):
        self.trapezf32 = np.float32(self.trapez)
        stretch_matrix = cv2.getPerspectiveTransform(self.trapezf32, self.stretch)
        self.current_img = cv2.warpPerspective(self.current_img, stretch_matrix, (self.width, self.height))

    def get_lines(self):

        upper_right = (self.width, 0)
        upper_left = (0, 0)
        lower_left = (0, self.height)
        lower_right = (self.width, self.height)
        corners = [upper_right, upper_left, lower_left, lower_right]

        # print(f'Lines: {final_edges}')
        # print(f'Board corners: {corners}')

        all_points = [[], [], [], []]
        # all_points[0] - upper_points
        # all_points[1] - left_points
        # all_points[2] - lower_points
        # all_points[3] - right_points

        for i in range(0, 4):
            all_points[i].append(corners[i])

        for i in range(1, 8):
            for j in range(0, 4):
                p_x = corners[j][0] + (corners[(j+1) % 4][0] - corners[j][0]) // 8 * i
                p_y = corners[j][1] + (corners[(j+1) % 4][1] - corners[j][1]) // 8 * i
                all_points[j].append([p_x, p_y])

        for i in range(0, 4):
            all_points[i].append(corners[(i+1) % 4])

        # for i in range(0, 4):
        #     print(f'All point[{i}]: {all_points[i]}')
        #     for j in range(1, 5):
        #         cv2.circle(self.current_img, all_points[i][j], 8, (255, 255, 255), -1)

        self.vertical_lines = [all_points[0][::-1], all_points[2]]
        self.horizontal_lines = [all_points[1], all_points[3][::-1]]

        self.corners = []
        for j in range(0, 9):
            for i in range(0, 9):
                v_line = self.vertical_lines[0][i] + self.vertical_lines[1][i]
                h_line = self.horizontal_lines[0][j] + self.horizontal_lines[1][j]
                inter_point = intersection(v_line, h_line)
                self.corners.append(inter_point)
                # print(f'Linie v[{i + 1}]{self.vertical_lines[0][i]} - {self.vertical_lines[1][i]}')
                # print(f'Linie h[{i + 1}]{self.horizontal_lines[0][j]} - {self.horizontal_lines[1][j]}')
                # print(f'Punct intersetie [{i}]{inter_point}')
                # cv2.circle(self.current_img, inter_point, 8, (255, 255, 255), -1)

        # for i in range(0, 81):
            # cv2.circle(self.current_img, self.corners[i], 8, (255, 255, 255), -1)

        # self.get_square(1, 8)

        self.show_grid()

    def print_current_image(self):
        cv2.imshow('Current image', self.current_img)

    def get_square_mean(self, x, y):
        if x in range(1, 9) and y in range(1, 9):
            x = x - 1
            y = y - 1
            coord = [self.corners[9 * x + y], self.corners[9 * x + y + 1],
                     self.corners[9 * (x + 1) + y], self.corners[9 * (x + 1) + y + 1]]
            points = np.array(coord, dtype=np.int32)

            cx, cy, cw, ch = cv2.boundingRect(points)
            cropped_image = self.current_img[cy:cy + ch, cx:cx + cw]
            middle_x = cw // 4
            middle_y = ch // 4
            middle_width = cw // 2
            middle_height = ch // 2

            middle_part = cropped_image[middle_y:middle_y + middle_height, middle_x:middle_x + middle_width]

            mean = int(np.mean(middle_part))
            # mean = int(np.mean(cropped_image))

            # copy = self.current_img.copy()
            # cv2.circle(copy, self.corners[9 * x + y], 8, (255, 255, 255), -1)
            # cv2.circle(copy, self.corners[9 * x + y + 1], 8, (255, 255, 255), -1)
            # cv2.circle(copy, self.corners[9 * (x + 1) + y], 8, (255, 255, 255), -1)
            # cv2.circle(copy, self.corners[9 * (x + 1) + y + 1], 8, (255, 255, 255), -1)
            # cv2.imshow('Corners', copy)
            #
            # wc = cropped_image.shape[1] * 4
            # hc = cropped_image.shape[0] * 4
            # cropped_image = cv2.resize(cropped_image, (wc, hc))
            #
            # wc = middle_part.shape[1] * 4
            # hc = middle_part.shape[0] * 4
            # middle_part = cv2.resize(middle_part, (wc, hc))
            #
            # cv2.imshow('Cropped Image', cropped_image)
            # cv2.imshow('Middle Cropped Image', middle_part)
            return mean

        print('Invalid position')
        return False

    def get_grid(self):
        for i in range(0, 8):
            for j in range(0, 8):
                med = self.get_square_mean(i+1, j+1)
                self.grid[i][j] = med
                # print(f'pos[{i}][{j}] = {med}')
        self.difgrid = abs(self.oldgrid - self.grid)
        # print(self.oldgrid)
        # print("/\ old")
        # print(self.grid)
        # print("/\ new")
        print(self.difgrid)
        print(np.mean(self.difgrid))
        # print("/\ diff")


if __name__ == "__main__":
    board = Board(img_init2)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
