"""Launch file for bipedal leg control system."""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """Generate launch description."""
    
    device_arg = DeclareLaunchArgument(
        'odrive_device',
        default_value='/dev/ttyACM0',
        description='ODrive USB device path'
    )
    
    control_rate_arg = DeclareLaunchArgument(
        'control_rate',
        default_value='100.0',
        description='Control loop rate in Hz'
    )
    
    upper_leg_arg = DeclareLaunchArgument(
        'upper_leg_length',
        default_value='0.3',
        description='Upper leg length in meters'
    )
    
    lower_leg_arg = DeclareLaunchArgument(
        'lower_leg_length',
        default_value='0.3',
        description='Lower leg length in meters'
    )
    
    leg_controller_node = Node(
        package='tfg_biped_leg',
        executable='leg_controller',
        name='leg_controller',
        parameters=[{
            'odrive_device': LaunchConfiguration('odrive_device'),
            'control_rate': LaunchConfiguration('control_rate'),
            'upper_leg_length': LaunchConfiguration('upper_leg_length'),
            'lower_leg_length': LaunchConfiguration('lower_leg_length'),
        }],
        output='screen',
        emulate_tty=True,
    )
    
    return LaunchDescription([
        device_arg,
        control_rate_arg,
        upper_leg_arg,
        lower_leg_arg,
        leg_controller_node,
    ])
