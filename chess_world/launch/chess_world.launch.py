# Copyright 2020 ros2_control Development Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from osrf_pycommon.terminal_color import ansi

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, RegisterEventHandler

from launch.conditions import IfCondition
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch.actions import IncludeLaunchDescription, TimerAction
from launch_ros.actions import Node

from launch.event_handlers import OnProcessExit
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource

def robot_spawn_nodes(id, xacro_name, pkg_path):
    # Get URDF via xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("chess_world"), "urdf", xacro_name]
            ),
        ]
    )

    robot_description = {"robot_description": robot_description_content}

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace=f'camera_{id}',
        output='screen',
        parameters=[robot_description]
    )

    # Spawn Robot
    spawn_entity = Node(
        package='gazebo_ros', 
        executable='spawn_entity.py',
        namespace=f'camera_{id}',
        arguments=[
            '-topic', 'robot_description',
            '-entity', f'd435_camera_{id}',
            '-x', str(0),
            '-y', str(0.0),
            '-Y', str(0.0),
        ],
        output='screen'
    )

    return [
        robot_state_publisher,
        spawn_entity,
    ]

def generate_launch_description():

    # gz model path edit
    gazebo_model_path = os.path.join(get_package_share_directory('chess_world'), 'models')
    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] += ":" + gazebo_model_path
    else :
        os.environ['GAZEBO_MODEL_PATH'] = gazebo_model_path
    print(ansi("yellow"), "If it's your 1st time to download Gazebo model on your computer, it may take few minutes to finish.", ansi("reset"))

    arg_show_rviz = DeclareLaunchArgument(
        "start_rviz",
        default_value="true",
        description="start RViz automatically with the launch file",
    )

    pkg_gazebo_ros = FindPackageShare(package='gazebo_ros').find('gazebo_ros')   
    pkg_path = os.path.join(get_package_share_directory('chess_world'))
    world_path = os.path.join(pkg_path, 'worlds', 'chesslab_simple.world')
    
    # Start Gazebo server
    start_gazebo_server_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
        launch_arguments={'world': world_path}.items()
    )

    # Start Gazebo client
    start_gazebo_client_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py'))
    )

    static_transform_publisher = Node(
        package = "tf2_ros",
        executable = "static_transform_publisher",
        arguments = ["0", "0", "0", "0", "0", "0", "world", "chess_frame"],
        condition=IfCondition(LaunchConfiguration("start_rviz"))
    )

    rviz_config_file = os.path.join(pkg_path, 'rviz', 'chess_world.rviz')
    
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config_file],
        condition=IfCondition(LaunchConfiguration("start_rviz"))
    )

    cam1_spawn = robot_spawn_nodes(0, "camera_left.urdf.xacro", pkg_path)
    cam2_spawn = robot_spawn_nodes(1, "camera_right.urdf.xacro", pkg_path)

    return LaunchDescription(
        [
            arg_show_rviz,
            start_gazebo_server_cmd,
            start_gazebo_client_cmd,
            static_transform_publisher,
            *cam1_spawn,
            *cam2_spawn,
            rviz_node,
        ]
    )
