#!/usr/bin/env python3
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Int32MultiArray


class IRSensorNode(Node):
    def __init__(self):
        super().__init__('ir_sensor_node')
        self.declare_parameter('black_threshold', 80)
        self.declare_parameter('patch_size', 12)
        self.black_thresh = self.get_parameter('black_threshold').value
        self.patch_size = self.get_parameter('patch_size').value
        self.sub_image = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )
        self.pub_ir = self.create_publisher(Int32MultiArray, '/ir_sensors', 10)
        self.get_logger().info('IR Sensor Node started')

    def sample_patch(self, gray, cx, cy):
        half = self.patch_size // 2
        h, w = gray.shape
        x0, x1 = max(0, cx - half), min(w, cx + half)
        y0, y1 = max(0, cy - half), min(h, cy + half)
        patch = gray[y0:y1, x0:x1]
        if patch.size == 0:
            return 255
        return int(np.mean(patch))

    def image_to_gray(self, msg):
        enc = msg.encoding.lower()
        channels_by_encoding = {
            'bgr8': 3,
            'rgb8': 3,
            'bgra8': 4,
            'rgba8': 4,
            'mono8': 1,
            '8uc1': 1,
        }
        channels = channels_by_encoding.get(enc)
        if channels is None:
            raise ValueError(f'Unsupported image encoding: {msg.encoding}')

        expected_step = msg.width * channels
        if msg.step < expected_step:
            raise ValueError(
                f'Image step {msg.step} is too small for {msg.width}x{channels}'
            )

        data = np.frombuffer(msg.data, dtype=np.uint8)
        row_stride = msg.step
        image = data.reshape((msg.height, row_stride))[:, :expected_step]
        if channels == 1:
            return image.reshape((msg.height, msg.width))

        image = image.reshape((msg.height, msg.width, channels))
        if enc == 'rgb8':
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        if enc == 'bgr8':
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if enc == 'rgba8':
            return cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
        return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)

    def image_callback(self, msg):
        try:
            gray = self.image_to_gray(msg)
        except ValueError as exc:
            self.get_logger().warn(str(exc), throttle_duration_sec=1.0)
            return

        h, w = gray.shape
        row_y = int(h * 0.85)
        left_x = int(w * 0.30)
        center_x = int(w * 0.50)
        right_x = int(w * 0.70)
        ir_left = 1 if self.sample_patch(gray, left_x, row_y) < self.black_thresh else 0
        ir_center = 1 if self.sample_patch(gray, center_x, row_y) < self.black_thresh else 0
        ir_right = 1 if self.sample_patch(gray, right_x, row_y) < self.black_thresh else 0
        msg_out = Int32MultiArray()
        msg_out.data = [ir_left, ir_center, ir_right]
        self.pub_ir.publish(msg_out)


def main(args=None):
    rclpy.init(args=args)
    node = IRSensorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
