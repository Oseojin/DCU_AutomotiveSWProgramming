import os
from glob import glob
from setuptools import setup

package_name = 'my_vehicle_description'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name] if os.path.exists(package_name) else [],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name] if os.path.exists('resource/' + package_name) else []),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.xacro') + glob('urdf/*.urdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Dongju Kim',
    maintainer_email='deekim@cu.ac.kr',
    description='Automotive SW Programming Week 3 - URDF/Xacro Vehicle Description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)
