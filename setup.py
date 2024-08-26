from setuptools import find_packages, setup

setup(
    name='myblockscoutlib',
    packages=find_packages(include=['myblockscoutlib']),
    version='0.3.0',
    description='A simple wallet watcher via Blockscout and CMC',
    author='Me',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==8.3.2'],
    test_suite='tests'
)