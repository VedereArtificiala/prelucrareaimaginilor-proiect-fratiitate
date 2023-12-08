import cv2
import numpy as np

director = 'images/'
imag = cv2.imread(director + 'img.png')
test_img = cv2.imread(director + 'img_1.png')
img_init = cv2.imread(director + 'init.png')
img_start = cv2.imread(director + 'start.png')
image1 = cv2.imread(director + 'move1.png')
image2 = cv2.imread(director + 'move2.png')
image3 = cv2.imread(director + 'move3.png')
image4 = cv2.imread(director + 'move4.png')
img_ill_1 = cv2.imread(director + 'illegal_move1.png')
img_ill_2 = cv2.imread(director + 'illegal_move2.png')

debug = True

class Board:

    def __init__(self, img, down_scale=2):
        self.previous_img = None
        self.board = None
        self.trapez = None
        self.trapezf32 = None
        self.width = img.shape[1] // down_scale
        self.height = img.shape[0] // down_scale
        self.current_img = cv2.resize(img, (self.width, self.height))
        self.current_img = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2GRAY)
        self.get_board_contour()
        self.stretch_board()
        self.set_lines()
        self.get_lines()
        if debug:
            cv2.imshow('Current Image', self.current_img)
            # cv2.imshow('Grayscale Image', self.current_img)

    def get_next_move(self, img):
        self.previous_img = self.current_img
        self.current_img = cv2.resize(img, (self.width, self.height))
        self.current_img = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2GRAY)
        self.current_img = self.current_img * self.board
        self.stretch_board()
        # self.get_lines()
        if debug:
            cv2.imshow('Current Image', self.current_img)
            cv2.imshow('Previous Image', self.previous_img)

    def get_board_contour(self):
        self.board = np.zeros((self.height, self.width), dtype=np.uint8)
        upper_right = (int(self.width * 0.74), int(self.height * 0.27))
        upper_left = (int(self.width * 0.29), int(self.height * 0.27))
        lower_left = (int(self.width * 0.24), int(self.height * 0.9))
        lower_right = (int(self.width * 0.79), int(self.height * 0.9))

        self.trapez = np.array([
            upper_right,
            upper_left,
            lower_left,
            lower_right
        ], dtype=np.int32)

        cv2.fillConvexPoly(self.board, self.trapez, 1)
        # cv2.imshow('Trapezoid', board * 255)
        self.current_img = self.current_img * self.board

    def get_current_image(self):
        return self.current_img

    def set_lines(self):
        pass
    def get_lines(self):
        kn = 3
        frame = cv2.blur(self.current_img, ksize=(kn, kn))
        edges = cv2.Canny(frame, 50, 150, apertureSize=3)
        if debug:
            cv2.imshow('Blured grayscale image', frame)
            cv2.imshow('Canny', edges)

        rho = 1  # distance resolution in pixels of the Hough grid
        theta = np.pi / 180  # angular resolution in radians of the Hough grid
        threshold = 15  # minimum number of votes (intersections in Hough grid cell)
        min_line_length = self.width // 6  # minimum number of pixels making up a line
        max_line_gap = self.width // 10  # maximum gap in pixels between connectable line segments
        line_image = np.copy(edges) * 0  # creating a blank to draw lines on

        # Run Hough on edge detected image
        # Output "lines" is an array containing endpoints of detected line segments
        lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                                min_line_length, max_line_gap)

        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), (255, 255, 255), 2)
        lines_edges = cv2.addWeighted(frame, 0.8, line_image, 1, 0)
        self.current_img = lines_edges
        if debug:
            print(lines)
            # cv2.imshow('LineDetection', self.current_img)

    def stretch_board(self):
        self.trapezf32 = np.float32(self.trapez)
        stretch = np.array([
            (self.width, 0),
            (0, 0),
            (0, self.height),
            (self.width, self.height)
        ], dtype=np.float32)
        stretch_matrix = cv2.getPerspectiveTransform(self.trapezf32, stretch)
        self.current_img = cv2.warpPerspective(self.current_img, stretch_matrix, (self.width, self.height))



if __name__ == "__main__":
    board = Board(img_init)

    board.get_lines()

    cv2.waitKey(0)
    cv2.destroyAllWindows()
