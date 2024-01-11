import cv2
import math


def calculate_angle(point, reference_point):
    x, y = point
    ref_x, ref_y = reference_point
    return math.atan2(y - ref_y, x - ref_x)


def sort_points(points, reference_point):
    return sorted(points, key=lambda point: calculate_angle(point, reference_point), reverse=True)


def line_length(line):
    return math.sqrt((line[2] - line[0]) ** 2 + (line[3] - line[1]) ** 2)


def extend_line(line, image_width, image_height):
    x1, y1, x2, y2 = line

    if x1 == x2:
        new_x1 = x1
        new_y1 = 0
        new_x2 = x1
        new_y2 = image_height - 1
    else:
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1

        new_x1 = 0
        new_y1 = int(intercept)
        new_x2 = image_width - 1
        new_y2 = int(slope * new_x2 + intercept)

        new_y1 = max(0, min(new_y1, image_height - 1))
        new_y2 = max(0, min(new_y2, image_height - 1))

    return new_x1, new_y1, new_x2, new_y2


def average_line(lines):
    s = 0
    sx1 = 0
    sx2 = 0
    sy1 = 0
    sy2 = 0
    for line in lines:
        s = s + 1
        x1, y1, x2, y2 = line
        sx1 = sx1 + x1
        sx2 = sx2 + x2
        sy1 = sy1 + y1
        sy2 = sy2 + y2

    return [sx1 // s, sy1 // s, sx2 // s, sy2 // s]


def line_equation(line):
    A = (line[1] - line[3])
    B = (line[2] - line[0])
    C = (line[0] * line[3] - line[2] * line[1])
    return A, B, -C


def intersection(line1, line2):
    L1 = line_equation(line1)
    L2 = line_equation(line2)
    D = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = int(Dx / D)
        y = int(Dy / D)
        return [x, y]
    else:
        return None


def intersections(lines):
    points = []
    length = len(lines)
    for i in range(0, length):
        line1 = lines[i - 1]
        line2 = lines[i]
        point = intersection(line1, line2)
        if point:
            # print(point)
            points.append(point)
    return points


def get_points(w_name, image):
    cv2.namedWindow(w_name)
    cv2.setMouseCallback(w_name, on_mouse_click)
    while True:
        # Display the image
        cv2.imshow(w_name, image)

        # Break the loop if 'ESC' key is pressed
        if cv2.waitKey(20) & 0xFF == 27:
            break


def on_mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked at position: ({x}, {y})")


def to_center(points, center, move_percent=0.05, k=0):
    a = 1 - move_percent
    b = move_percent
    new_points = []
    for point in points:
        new_x = int(a * point[0] + b * center[0] + k)
        new_y = int(a * point[1] + b * center[1] + k)
        new_points.append((new_x, new_y))

    for i in range(len(new_points)):
        if new_points[i][0] > center[0] and new_points[i][1] < center[1]:
            new_points = new_points[i:] + new_points[:i]
            break
    return new_points

# Lines = [[0, 16, 639, 16], [14, 0, 14, 479], [0, 468, 639, 468], [622, 0, 622, 479]]
# # [[14, 16], [622, 16], [14, 468], [622, 468]]
# P = intersections(Lines)
# if P:
#     print("Intersection detected:", P)
# else:
#     print("No single intersection point detected")
