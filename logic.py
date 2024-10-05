import time
from lane_line_detection import find_lane_lines, birdview_transform, find_left_right_points

class CarLogic:
    def __init__(self):
        self.last_sign = ''
        self.sign_until = 0
        self.stop = False 
        self.default_throttle = 0.3
        self.throttle = self.default_throttle
        self.steering_angle = 0

    def calculate_control_signal(self, img, draw=None):
        """Tính toán tốc độ và góc lái dựa trên đường kẻ và biển báo giao thông."""
        img_lines = find_lane_lines(img)
        img_birdview = birdview_transform(img_lines)
        if draw is not None:
            draw[:, :] = birdview_transform(draw)
            self.img_birdview = draw
        left_point, right_point = find_left_right_points(img_birdview, draw=draw)

        self.throttle = self.default_throttle
        steering_angle = 0
        im_center = img.shape[1] // 2

        if left_point != -1 and right_point != -1:
            center_point = (right_point + left_point) // 2
            center_diff = im_center - center_point
            steering_angle = -float(center_diff * 0.02) 
        else:
            steering_angle = 0
        self.steering_angle = steering_angle

    def detect_sign(self, signs):
        """Phát hiện biển báo 'left' hoặc 'stop'."""

        for sign in signs:
            class_name = sign[0]
            if class_name in [ 'stop']:
                self.last_sign = class_name
                if class_name == 'stop':
                    self.sign_until = time.time() + 2  
                print(f"Detected sign: {class_name}")
                print(f"handle {class_name}")
                break  # Chỉ xử lý biển báo đầu tiên
        else:
            self.last_sign = ''

    def handle_sign(self):
        """Xử lý hành động dựa trên biển báo đã phát hiện."""

        current_time = time.time()
        if self.last_sign == 'stop':
            if current_time < self.sign_until:
                self.throttle = 0
                self.steering_angle = 0
                print("Car is stopping...")
            else:
                self.last_sign = ''

    def decision_control(self, image, signs, draw):
        """Quy trình điều khiển chính để xử lý hình ảnh và biển báo."""

        self.calculate_control_signal(image, draw)
        self.detect_sign(signs)
        self.handle_sign()

        print(f"Throttle: {self.throttle} -- Steering Angle: {self.steering_angle}")
        return self.throttle, self.steering_angle