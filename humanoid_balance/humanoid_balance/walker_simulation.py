import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64, Header
import math
import time

class BipedWalker(Node):
    def __init__(self):
        super().__init__('biped_walker')
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # New Subscriber: Listen to balance corrections from your BalanceNode
        self.correction_sub = self.create_subscription(
            Float64,
            '/torso_correction',
            self.correction_callback,
            10
        )
        
        self.timer = self.create_timer(0.02, self.generate_walk_gait)
        
        self.joint_names = [
            'left_hip_joint', 'left_knee_joint', 'left_ankle_joint',
            'right_hip_joint', 'right_knee_joint', 'right_ankle_joint'
        ]
        self.start_time = time.time()
        self.torso_offset = 0.0 # Stores live adjustment value

    def correction_callback(self, msg):
        # Update our offset whenever BalanceNode calculates a lean requirement
        self.torso_offset = msg.data

    def generate_walk_gait(self):
        t = time.time() - self.start_time
        
        frequency = 1.5    
        amplitude = 0.4    
        omega = 2.0 * math.pi * frequency
        
        # Base gait math
        left_hip = amplitude * math.sin(omega * t)
        right_hip = amplitude * math.sin(omega * t + math.pi)
        
        left_knee = abs(amplitude * 1.5 * math.sin(omega * t)) if left_hip < 0 else 0.0
        right_knee = abs(amplitude * 1.5 * math.sin(omega * t + math.pi)) if right_hip < 0 else 0.0
        
        left_ankle = -left_hip * 0.5
        right_ankle = -right_hip * 0.5

        # --- APPLY BALANCING OFFSET ---
        # Injecting the correction bias directly into hips and ankles 
        # to force the upper body to tilt/compensate dynamically
        left_hip += self.torso_offset
        right_hip += self.torso_offset
        left_ankle -= self.torso_offset
        right_ankle -= self.torso_offset

        msg = JointState()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = [left_hip, left_knee, left_ankle, right_hip, right_knee, right_ankle]
        
        self.joint_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = BipedWalker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()