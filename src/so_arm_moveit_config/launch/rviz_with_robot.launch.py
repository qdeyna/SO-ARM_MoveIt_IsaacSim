from pathlib import Path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, RegisterEventHandler
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder
from launch.event_handlers import OnProcessStart

from launch_ros.parameter_descriptions import ParameterFile

moveit_controllers_yaml = ParameterFile(
    PathJoinSubstitution([
        FindPackageShare("so_arm_moveit_config"),
        "config",
        "moveit_controllers.yaml"
    ]),
    allow_substs=True
)

def generate_launch_description():
    declared_arguments = []
    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )


def launch_setup(context, *args, **kwargs):
    current_file_path = Path(__file__).resolve()
    current_directory = str(current_file_path.parent)

    use_sim_time = {"use_sim_time": True}
    
    # Configure MoveIt
    moveit_config = (
        MoveItConfigsBuilder("so_arm_description", package_name="so_arm_moveit_config")
        .robot_description(file_path="config/so_arm_urdf.urdf.xacro")
        .robot_description_semantic(file_path=str(Path(get_package_share_directory('so_arm_description')) / 'srdf' / 'so_arm_urdf.srdf'))
        .planning_pipelines(
            pipelines=["ompl", "chomp", "pilz_industrial_motion_planner"]
        )
        .planning_scene_monitor(
            publish_robot_description=True,
            publish_robot_description_semantic=True
        )
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .to_moveit_configs()
    )

    # Load Controllers
    robot_description = moveit_config.robot_description
    controllers_config = str(Path(get_package_share_directory('so_arm_moveit_config')) / 'config' / 'ros2_controllers.yaml')

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            robot_description,
            controllers_config,
        ],
        output="both",
    )

    # Start controllers
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller", "--controller-manager", "/controller_manager"],
    )

    # Start the actual move_group node/action server
    run_move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
            moveit_config.planning_pipelines,
            moveit_config.trajectory_execution, 
            use_sim_time,
        ],
    )

    # RViz configuration
    rviz_config = PathJoinSubstitution(
        [FindPackageShare("so_arm_moveit_config"), "config", "moveit.rviz"]
    )

    # RViz node
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
            moveit_config.planning_pipelines
        ],
    )

    # Static TF
    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        output="log",
        arguments=["0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "world", "Base"],
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[moveit_config.robot_description],
    )

    # Joint State Publisher GUI
    joint_state_publisher_gui = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        output="log",
    )

    # Make sure controllers start after move_group to avoid race conditions
    controller_spawner_depends_on_move_group = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=run_move_group_node,
            on_start=[
                joint_state_broadcaster_spawner,
                arm_controller_spawner,
            ],
        )
    )

    nodes_to_start = [
        control_node,
        rviz_node,
        static_tf,
        robot_state_publisher,
        joint_state_publisher_gui,
        run_move_group_node,
        controller_spawner_depends_on_move_group,
    ]

    return nodes_to_start 