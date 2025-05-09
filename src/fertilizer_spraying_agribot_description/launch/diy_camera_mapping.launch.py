import os

from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
import launch_ros.actions

from launch import LaunchDescription
from launch_ros.actions import Node, SetParameter
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    parameters={
          'frame_id':'fertilizer_bot/base_link',
          'approx_sync':False,
          'subscribe_depth':True,
          'Reg/Force3DoF':'true',
          'Optimizer/GravitySigma':'0',
          'odom_frame_id':'fertilizer_bot/odom',
          'database_path':'database/real.db',
          'RGBD/Octomap':True,
          'Grid/Sensor':'1',
          'Vis/MinInliers':'100'
    }

    remappings=[
          ('/fertilizer_bot/rgb/image', '/fertilizer_bot/fertilizer_bot_camera/left/image_rect_color'),
          ('/fertilizer_bot/rgb/camera_info', '/fertilizer_bot/fertilizer_bot_camera/left/camera_info'),
          ('/fertilizer_bot/depth/image', '/depth')]
    
    use_sim_time = LaunchConfiguration('use_sim_time')
    qos = LaunchConfiguration('qos')
    localization = LaunchConfiguration('localization')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', default_value='false',
            description='Use simulation (Gazebo) clock if true'),

        DeclareLaunchArgument(
            'qos', default_value='2',
            description='QoS used for input sensor topics'),

        DeclareLaunchArgument(
            'localization', default_value='false',
            description='Launch in localization mode.'),
        Node(
            namespace='/camera_left',package='v4l2_camera',executable='v4l2_camera_node',
            parameters=[{'video_device':'/dev/video4'},
                        {'camera_info_url':'file:///home/don/Project_Agribot/src/fertilizer_spraying_agribot_description/config/left.yaml'},
                        # {'image_size':[848,580]},
                        {'camera_frame_id':'fertilizer_bot_camera_color_frame'}]
        ),

        Node(
            namespace='/camera_right',package='v4l2_camera',executable='v4l2_camera_node',
            parameters=[{'video_device':'/dev/video2'},
                        {'camera_info_url':'file:///home/don/Project_Agribot/src/fertilizer_spraying_agribot_description/config/right.yaml'},
                        # {'image_size':[1920,1080]},
                        {'camera_frame_id':'fertilizer_bot_camera_color_frame'}]
        ),

        Node(
            package='fertilizer_spraying_agribot_description',executable='camera_sync'),
        
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory('stereo_image_proc'), 'launch'),'/stereo_image_proc.launch.py']),
                launch_arguments={'left_namespace':'fertilizer_bot/fertilizer_bot_camera/left',
                                  'P1':'240.0',
                                  'P2':'400.0',
                                  'stereo_algorithm':'1',
                                  'disparity_range':'80',
                                  'min_disparity':'4',
                                  'correlation_window_size':'7',
                                  'texture_threshold':'0',
                                  'approximate_sync':'false',
                                  'use_color':'true',
                                  'uniqueness_ratio':'7.0',
                                  'speckle_size':'800',
                                  'speckle_range':'1',
                                  'disp12_max_diff':'70',
                                  'right_namespace':'fertilizer_bot/fertilizer_bot_camera/right'}.items(),
        ),
        # Node(
        #     package='fertilizer_spraying_agribot_description',executable='stereo'),

        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource([os.path.join(
        #         get_package_share_directory('rtabmap_launch'), 'launch'),'/rtabmap.launch.py']),
        #         launch_arguments={'frame_id':'fertilizer_bot/base_link',
        #                             'namespace':'fertilizer_bot',
        #                             'rgb_topic':'/fertilizer_bot/fertilizer_bot_camera/left/image_rect_color',
        #                             'rtabmap_viz':'true',
        #                             'depth_topic':'/depth',
        #                             'approx_sync':'true',
        #                             'camera_info_topic':'/fertilizer_bot/fertilizer_bot_camera/left/camera_info',
        #                             'vo_frame_id':'/fertilizer_bot/visual_odom',
        #                             'Reg/Force3DoF':'true',
        #                             'rviz':'true',
        #                             'queue_size':'30',
        #                             'Vis/MinInliers':'100',
        #                             'Optimizer/GravitySigma':'0',
        #                             'database_path':'database/real.db',
        #                             'publish_tf_odom':'true'}.items(),
        # ),
        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource([os.path.join(
        #         get_package_share_directory('rtabmap_launch'), 'launch'),'/rtabmap.launch.py']),
        #         launch_arguments={'frame_id':'fertilizer_bot/base_link',
        #                             'namespace':'fertilizer_bot',
        #                             'stereo':'true',
        #                             'cfg':'rtabmap.ini',
        #                             'left_image_topic':'/fertilizer_bot/fertilizer_bot_camera/left/image_rect',
        #                             'rtabmap_viz':'true',
        #                             'right_image_topic':'/fertilizer_bot/fertilizer_bot_camera/right/image_rect',
        #                             'approx_sync':'true',
        #                             'left_camera_info':'/left/camera_info',
        #                             'right_camera_info':'/right/camera_info',
        #                             'vo_frame_id':'/fertilizer_bot/visual_odom',
        #                             'Reg/Force3DoF':'true',
        #                             'rviz':'true',
        #                             'Vis/MinInliers':'100',
        #                             'Optimizer/GravitySigma':'0',
        #                             'database_path':'database/real.db',
        #                             'stereo_namespace':'fertilizer_bot_camera',
        #                             'publish_tf_odom':'true'}.items(),
        # ),
        launch_ros.actions.Node(
            package='robot_localization',
            executable='ekf_node',
            namespace='fertilizer_bot',
            output='screen',
            parameters=[os.path.join(get_package_share_directory("fertilizer_spraying_agribot_description"), 'config', 'ekf.yaml')],
            remappings=[('/fertilizer_bot/odometry/filtered','/fertilizer_bot/odom')]
        ),
        Node(
            condition=UnlessCondition(localization),
            namespace='fertilizer_bot',
            package='rtabmap_slam', executable='rtabmap', output='screen',
            parameters=[parameters],
            remappings=remappings,
            arguments=['-d']), # This will delete the previous database (~/.ros/rtabmap.db)

        # Localization mode:
        Node(
            condition=IfCondition(localization),
            namespace='fertilizer_bot',
            package='rtabmap_slam', executable='rtabmap', output='screen',
            parameters=[parameters,
              {'Mem/IncrementalMemory':'False',
               'Mem/InitWMWithAllNodes':'True'}],
            remappings=remappings),
        
        Node(
            package='rtabmap_viz', executable='rtabmap_viz', output='screen', namespace='fertilizer_bot',
            parameters=[parameters],
            remappings=remappings),
        
        Node (package='rtabmap_util', executable='disparity_to_depth', output='screen'),
        
        Node(
            package='rtabmap_odom', executable='rgbd_odometry', output='screen',
            namespace='fertilizer_bot',
            parameters=[{'frame_id':'fertilizer_bot/base_link'},
                        {'approx_sync':False},
                        {'odom_frame_id':'fertilizer_bot/odom'},
                        {'publish_tf':True},
                        {'Reg/Force3DoF':'true'},
                        {'Optimizer/GravitySigma':'0'},
                        {'RGBD/Octomap':True},
                        {'Grid/Sensor':'1'}],
            remappings=[('/fertilizer_bot/rgb/image', '/fertilizer_bot/fertilizer_bot_camera/left/image_rect_color'),
                        ('/fertilizer_bot/rgb/camera_info', '/fertilizer_bot/fertilizer_bot_camera/left/camera_info'),
                        ('/fertilizer_bot/depth/image', '/depth'),
                        ('odom', '/fertilizer_bot/visual_odom')]),
])
