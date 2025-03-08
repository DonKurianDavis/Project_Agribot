from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'multibot_navigation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'world'), glob('world/*')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*'))

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='don',
    maintainer_email='donmundadan321@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'plant_points = multibot_navigation.plant_points:main',
            'harvesting_goal_navigator = multibot_navigation.harvesting_goal_navigator:main',
            'fertilizer_goal_navigator = multibot_navigation.fertilizer_goal_navigator:main',
        ],
    },
)
