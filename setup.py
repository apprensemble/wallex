from setuptools import find_packages, setup

setup(
    name='wallex',
    packages=find_packages(include=['wallex']),
    version='0.3.5',
    description='A simple wallet watcher via Blockscout,moralis and CMC',
    author='CryptoGrillon',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==8.3.2'],
    test_suite='tests'
)