from setuptools import find_packages, setup

setup(
    name='wb-mqtt-topic-manager',
    version='0.1.0',
    author='Valerii Trofimov',
    description='Python module (library) for working with an MQTT broker, which fully encapsulates topic logic in accordance with the Wiren Board convention',
    packages=find_packages(),
    install_requires=[
        'paho-mqtt==2.1.0',
        'pytest==9.0.1',
        'pytest-asyncio==1.3.0',
    ],
    python_requires='>=3.13',
)
