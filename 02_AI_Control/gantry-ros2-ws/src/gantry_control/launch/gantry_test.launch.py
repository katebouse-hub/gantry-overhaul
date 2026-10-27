from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    delay_arg = DeclareLaunchArgument(
        'move_delay',
        default_value='1.0',
        description='Simulated move delay in seconds',
    )

    state_manager = Node(
        package='gantry_control',
        executable='state_manager_node',
        name='state_manager_node',
        output='screen',
    )

    dummy_server = Node(
        package='gantry_control',
        executable='gantry_move_server_node',
        name='gantry_move_server_node',
        output='screen',
        parameters=[{
            'move_delay': LaunchConfiguration('move_delay'),
        }],
    )

    return LaunchDescription([delay_arg, state_manager, dummy_server])
