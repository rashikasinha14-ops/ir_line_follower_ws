#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray
from geometry_msgs.msg import Twist

class IRControllerNode(Node):
    def __init__(self):
        super().__init__('ir_controller_node')
        self.declare_parameter('linear_speed',    0.15)
        self.declare_parameter('turn_speed_soft', 0.4)
        self.declare_parameter('turn_speed_hard', 0.8)
        self.declare_parameter('search_speed',    0.5)
        self.v_lin    = self.get_parameter('linear_speed').value
        self.v_soft   = self.get_parameter('turn_speed_soft').value
        self.v_hard   = self.get_parameter('turn_speed_hard').value
        self.v_search = self.get_parameter('search_speed').value
        self.last_turn_dir = 1.0
        self.sub_ir  = self.create_subscription(Int32MultiArray, '/ir_sensors', self.ir_callback, 10)
        self.pub_cmd = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('IR Controller Node started')

    def ir_callback(self, msg):
        L, C, R = msg.data
        cmd = Twist()
        if   (L, C, R) == (0, 1, 0):
            cmd.linear.x  = self.v_lin
            cmd.angular.z = 0.0
        elif (L, C, R) == (1, 1, 0):
            cmd.linear.x  = self.v_lin * 0.7
            cmd.angular.z = self.v_soft
            self.last_turn_dir = 1.0
        elif (L, C, R) == (1, 0, 0):
            cmd.linear.x  = self.v_lin * 0.4
            cmd.angular.z = self.v_hard
            self.last_turn_dir = 1.0
        elif (L, C, R) == (0, 1, 1):
            cmd.linear.x  = self.v_lin * 0.7
            cmd.angular.z = -self.v_soft
            self.last_turn_dir = -1.0
        elif (L, C, R) == (0, 0, 1):
            cmd.linear.x  = self.v_lin * 0.4
            cmd.angular.z = -self.v_hard
            self.last_turn_dir = -1.0
        elif (L, C, R) == (1, 1, 1):
            cmd.linear.x  = self.v_lin
            cmd.angular.z = 0.0
        elif (L, C, R) == (1, 0, 1):
            cmd.linear.x  = self.v_lin
            cmd.angular.z = 0.0
        else:
            cmd.linear.x  = 0.0
            cmd.angular.z = self.v_search * self.last_turn_dir
            self.get_logger().warn('Line lost - searching...', throttle_duration_sec=1.0)
        self.pub_cmd.publish(cmd)

    def destroy_node(self):
        self.pub_cmd.publish(Twist())
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = IRControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()