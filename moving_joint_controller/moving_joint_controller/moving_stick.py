import math
import rclpy  # Import the ROS client library for Python
from rclpy.node import Node  # Enables the use of rclpy's Node class

from std_msgs.msg import (
    Float64,
    Float64MultiArray,
)  # Enable use of the std_msgs/Float64MultiArray message type

# Twist Sub => Float64MultiArray Pub
class JointController(Node):
    def __init__(self):
        super().__init__("joint_controller")

        self.steering_pub = self.create_publisher(
            Float64MultiArray, "/forward_position_controller/commands", 10
        )

        self.timer = self.create_timer(0.3, self.timer_cb)

        self.steering_msg = Float64MultiArray()
        self.data = 0.0

    def timer_cb(self):
        
        self.data += 0.03
        self.steering_msg.data = [self.data]
        self.steering_pub.publish(self.steering_msg)

def main(args=None):

    rclpy.init(args=args)

    joint_controller = JointController()
    rclpy.spin(joint_controller)
    joint_controller.destroy_node()

    rclpy.shutdown()

if __name__ == "__main__":
    main()