from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'gantry_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config',
            glob('config/*.json')),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vandal',
    maintainer_email='vandal@todo.todo',
    description='ROS2 client nodes for gantry control',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'state_manager_node = gantry_control.state_manager_node:main',
            'gantry_move_client_node = gantry_control.gantry_move_client_node:main',
            'state_client_node = gantry_control.state_client_node:main',
            'gantry_move_server_node = gantry_control.gantry_move_server_node:main',
            'gantry_mcp_server = gantry_control.gantry_mcp_server:main',
        ],
    },
)
