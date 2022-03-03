"setup.py"

import setuptools # type: ignore

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

NAME = 'training_manager'
AUTHOR = 'Urasaki Keisuke'
AUTHOR_EMAIL = 'urasakikeisuke.ml@gmail.com'
LICENSE = 'MIT License'
VERSION = "0.1.0"
PYTHON_REQUIRES = ">=3.6"
INSTALL_REQUIRES = [
    "slack-sdk==3.11.2",
]
PACKAGES = setuptools.find_packages()
CLASSIFIERS =[
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3 :: Only',
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

setuptools.setup(
    name=NAME,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    long_description=LONG_DESCRIPTION,
    license=LICENSE,
    version=VERSION,
    python_requires=PYTHON_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    packages=PACKAGES,
    classifiers=CLASSIFIERS
)
