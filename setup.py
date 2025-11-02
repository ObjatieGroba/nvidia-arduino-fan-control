from setuptools import setup
import os

_here = os.path.abspath(os.path.dirname(__file__))

package_name = 'nvidia_arduino_fan_control'

version = {}
with open(os.path.join(_here, package_name, 'version.py')) as f:
    exec(f.read(), version)

setup(
    name=package_name,
    version=version['__version__'],
    description='PC Fan control depends on nvidia cards temp sensors',
    long_description='',
    author='Igor Mineev',
    author_email='mineev@optain.ru',
    license='',
    packages=[package_name],
    install_requires=[],
    package_data={
        package_name: ['*.ino', '*.json']
    },
    )
