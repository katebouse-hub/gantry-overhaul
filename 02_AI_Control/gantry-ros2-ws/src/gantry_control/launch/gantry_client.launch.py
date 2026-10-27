from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    state_manager = Node(
        package='gantry_control',
        executable='state_manager_node',
        name='state_manager_node',
        output='screen',
    )

    return LaunchDescription([state_manager])
