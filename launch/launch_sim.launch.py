import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    package_name = 'pirover'

    # 1. Robot State Publisher
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
        )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # 2. Include the Gazebo Sim launch file (Replaces gazebo_ros)
    # This starts the Gazebo Harmonic engine
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': '-r empty.sdf'}.items() # -r runs it immediately
    )

    # 3. Run the spawn node (Replaces spawn_entity.py)
    # In Jazzy/Harmonic, the executable is 'create' and uses '-name'
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-name', 'my_bot',
                   '-z', '0.1'], # Spawning slightly above ground helps avoid clipping
        output='screen'
    )

    # 4. Bridge (REQUIRED for Jazzy)
    # Gazebo and ROS 2 use different transport protocols now. 
    # This node maps the /tf and /scan (if you have a lidar) etc.
    # At minimum, you usually need a bridge for clock if using sim time.
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        # Map Gazebo odom to ROS odom
        '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
        # Map Gazebo transforms to ROS tf
        '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        # ADD THIS FOR WHEELS:
        '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model'
        ],
        output='screen'
    )

    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        bridge
    ])
