from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    plc_host_arg = DeclareLaunchArgument(
        'plc_host',
        default_value='127.0.0.1',
        description='Modbus PLC host IP',
    )
    plc_port_arg = DeclareLaunchArgument(
        'plc_port',
        default_value='5020',
        description='Modbus PLC TCP port',
    )

    state_manager = Node(
        package='gantry_control',
        executable='state_manager_node',
        name='state_manager_node',
        output='screen',
    )

    gantry_command = Node(
        package='gantry_control',
        executable='gantry_command_node',
        name='gantry_command_node',
        output='screen',
        parameters=[{
            'plc_host': LaunchConfiguration('plc_host'),
            'plc_port': LaunchConfiguration('plc_port'),
        }],
    )

    return LaunchDescription([
        plc_host_arg,
        plc_port_arg,
        state_manager,
        gantry_command,
    ])
