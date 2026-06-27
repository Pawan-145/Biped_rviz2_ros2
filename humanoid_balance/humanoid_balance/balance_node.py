import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import Int16, String, Float64
from std_srvs.srv import Trigger
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import time
import math

class BalanceNode(Node):
    def __init__(self):
        super().__init__("balance_hub")

        # 1. Callback Groups
        self.group_a = ReentrantCallbackGroup()
        self.group_b = MutuallyExclusiveCallbackGroup()

        # 2. State Variables
        self.calculated_pitch_error = 0.0  # Initialized to avoid AttributeError
        self.start_time = time.time()

        # 3. Publishers & Subscribers
        sensor_qos = qos_profile_sensor_data
        self.publisher_ = self.create_publisher(Int16, "/imu/data", sensor_qos)
        self.publisher_joint_states = self.create_publisher(String, "/target_joint_states", sensor_qos, callback_group=self.group_a)
        self.publisher_torso = self.create_publisher(Float64, '/torso_correction', sensor_qos)
        
        self.subscriber_ = self.create_subscription(Int16, "/imu/data", self.listen_callback, sensor_qos, callback_group=self.group_a)
        self.srv_ = self.create_service(Trigger, "/calibrate_imu", self.callback_service)
        
        # 4. Timers
        self.timer_ = self.create_timer(0.01, self.callback_pub, callback_group=self.group_a)
        self.footstep_timer = self.create_timer(2.0, self.calculate_footstep, callback_group=self.group_b)
        self.toso_timer = self.create_timer(1.0, self.torso_callback)

    def callback_pub(self):
        msg = Int16()
        msg.data = 4
        self.publisher_.publish(msg)
        self.get_logger().info("Publishing IMU simulation heartbeat...")

        joint_msg = String()
        joint_msg.data = "MOVE_LEGS_BALANCED"
        self.publisher_joint_states.publish(joint_msg)

        # MOCK IMU PITCH DETECTION: 
        # Simulating a slow, drift oscillation so you can watch the robot lean 
        # forward and backward dynamically over time in RViz
        elapsed = time.time() - self.start_time
        self.calculated_pitch_error = 0.3 * math.sin(0.5 * elapsed)
    
    def listen_callback(self, msg):
        self.get_logger().info(f"Received IMU data stream: {msg.data}")
        
    def callback_service(self, request, response):
        self.get_logger().info("Calibrating IMU... Please hold robot steady.")
        response.success = True
        response.message = "Calibration complete!"
        return response
     
    def calculate_footstep(self):
        time.sleep(1.0) # Long running task safely isolated in Group B
        self.get_logger().info("Footstep Planned!")
    
    def torso_callback(self):
        msg = Float64()
        # Scale down and invert the error to steady the upper body frame
        msg.data = self.calculated_pitch_error * -0.5 
        
        # FIXED: Changed from correction_publisher to publisher_torso
        self.publisher_torso.publish(msg)
        self.get_logger().info(f"Sent correction angle to legs: {msg.data:.4f} rad")

def main(args=None):
    rclpy.init(args=args)
    node = BalanceNode()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()