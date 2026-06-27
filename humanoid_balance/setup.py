from setuptools import find_packages, setup

package_name = 'humanoid_balance'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='humanoid',
    maintainer_email='pawankrai145@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "balance_node = humanoid_balance.balance_node:main",
            "joint_controller = humanoid_balance.joint_controller:main",
            "walker = humanoid_balance.walker_simulation:main"
        ],
    },
)
