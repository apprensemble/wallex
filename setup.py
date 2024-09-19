from setuptools import find_packages, setup

setup(
    name='wallex',
    packages=find_packages(include=['wallex']),
    version='0.5.9.2',
    description='A simple wallet watcher via Blockscout,moralis and CMC',
    author='CryptoGrillon',
    install_requires=['selenium','requests','typing','pandas'],
    extras_require={
        'tests': ['pytest'],
    },
)
# pip install setuptools
# pip install pytest
# pip install wheel
# lancement build : python setup.py bdist_wheel
# lancement tests : pytest
# installation : pip install dist/wallex-version