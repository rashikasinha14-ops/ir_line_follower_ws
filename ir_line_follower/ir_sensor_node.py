#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Int32MultiArray
from cv_bridge import CvBridge
import cv2
import numpy as np

class IRSensorNode(Node):
    def __init__(self):
        super().__init__('ir_sensor_node')
        self.declare_parameter('black_threshold', 80)
        self.declare_parameter('patch_size', 12)
        self.black_thresh = self.get_parameter('black_threshold').value
        self.patch_size   = self.get_parameter('patch_size').value
        self.bridge = CvBridge()
        self.sub_image = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.pub_ir    = self.create_publisher(Int32MultiArray, '/ir_sensors', 10)
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

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w  = gray.shape
        row_y    = int(h * 0.85)
        left_x   = int(w * 0.30)
        center_x = int(w * 0.50)
        right_x  = int(w * 0.70)
        ir_left   = 1 if self.sample_patch(gray, left_x,   row_y) < self.black_thresh else 0
        ir_center = 1 if self.sample_patch(gray, center_x, row_y) < self.black_thresh else 0
        ir_right  = 1 if self.sample_patch(gray, right_x,  row_y) < self.black_thresh else 0
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