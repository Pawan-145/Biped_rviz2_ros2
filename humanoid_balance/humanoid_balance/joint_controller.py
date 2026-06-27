import rclpy
from rclpy.lifecycle import TransitionCallbackReturn,State, LifecycleNode
from std_msgs.msg import String, Int16
from rclpy.qos import qos_profile_sensor_data

class ManagerNode(LifecycleNode):
    def __init__(self):
        super().__init__("joint_controller")
        self.pub_ = None
        

    def on_configure(self, state):
        sensor_qos = qos_profile_sensor_data
        self.get_logger().info("Leg motors configured.")
        self.pub_ = self.create_lifecycle_publisher(String,"/imu/data",10)
        self.sub = self.create_subscription(String, "/target_joint_states", self.joint_command_callback, sensor_qos)
        return TransitionCallbackReturn.SUCCESS
    
    def joint_command_callback(self,msg):
        self.get_logger().info(f"Executing Motor Command: {msg.data}")
    
    def on_activate(self, state):
        self.get_logger().info("Leg motors armed and ready!")
        return TransitionCallbackReturn.SUCCESS
    
    def on_deactivate(self, state):
        self.get_logger().info("Leg motors are deactivated")
        return TransitionCallbackReturn.SUCCESS
    
    def on_cleanup(self, state):
        self.get_logger().info("Cleaning up...")
        return TransitionCallbackReturn.SUCCESS
    def on_shutdown(self, state):
        self.get_logger().info("Shutting Down....")
        return TransitionCallbackReturn.SUCCESS




def main(args=None):
    rclpy.init(args=args)
    node = ManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()