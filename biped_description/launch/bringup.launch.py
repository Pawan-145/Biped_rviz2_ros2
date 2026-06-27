import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Get package paths
    biped_desc_share = get_package_share_directory('biped_description')
    
    # 2. Include your existing RViz2 display launch file
    rviz_display = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(biped_desc_share, 'launch', 'display.launch.py')
        )
    )

    # 3. Add your Walker Simulation Node
    walker_simulation_node = Node(
        package='humanoid_balance',
        executable='walker',
        name='walker_simulation',
        output='screen'
    )

    # 4. Add your Main Balance Hub Node
    balance_hub_node = Node(
        package='humanoid_balance',
        executable='balance_node',
        name='balance_node',
        output='screen'
    )

    # Combine everything into a single execution layout
    return LaunchDescription([
        rviz_display,
        walker_simulation_node,
        balance_hub_node
    ])