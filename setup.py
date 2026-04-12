from setuptools import setup

package_name = 'tfg_biped_leg'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/bringup.launch.py']),
        ('share/' + package_name + '/config', [
            'config/hip.yaml',
            'config/knee.yaml',
            'config/ankle.yaml',
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pi',
    maintainer_email='pi@raspberrypi',
    description='Bipedal robot leg control using ODrive motor controllers',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'leg_controller = tfg_biped_leg.leg_controller:main',
            'test_leg = scripts.test_leg:main',
            'calibrate_motors = scripts.calibrate_motors:main',
        ],
    },
)
