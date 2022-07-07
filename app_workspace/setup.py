from setuptools import setup, find_packages
import os


setup( 
    name="jaws-optimizer",
    version="0.2",
    author="LiberyLab",
    author_email="contacto@libery-labs.com",
    description="a cli tool to create images srcsets",
    maintainer="Gerardo Rodriguez Sanchez",
    maintainer_email="gerardo.rodriguez@liberylabs.com",
    install_requires=["Pillow", "click"],
    license="LGPL-2.1-only",
    # package_dir={'': 'src'},
    packages=find_packages(),
    entry_points='''
    [console_scripts]
    jaws=Jaws:cli
    '''
)
