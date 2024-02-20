# Write a setup
from setuptools import setup, find_packages

from setuptools import setup, find_packages

setup(
    name='ADDU',
    version='0.1.5',
    author='Diego Delgado Chaves',
    author_email='diedelcha@gmail.com',
    description='ADDU is a cli tool for creating and managing Dockerized ROS Environments',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Daiego43/ADDU',
    packages=find_packages(),
    install_requires=[
        # Aquí puedes listar las dependencias de tu proyecto, por ejemplo:
        'certifi>=2024.2.2',
        'charset-normalizer>=3.3.2',
        'docker>=7.0.0',
        'idna>=3.6',
        'markdown-it-py>=3.0.0',
        'mdurl>=0.1.2',
        'packaging>=23.2',
        'Pygments>=2.17.2',
        'PyYAML>=6.0.1',
        'requests>=2.31.0',
        'rich>=13.7.0',
        'urllib3>=2.2.0'

    ],
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'addu-cli=ADDU.main:addu_cli'
        ],
    },
)
