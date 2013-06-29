try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
        name="PyPump",
        version="0.1a",
        description="Python Pump.io library",
        long_description=open("README.rst").read(),
        author="Jessica Tallon",
        author_email="tfmyz@inboxen.org",
        url="https://github.com/xray7224/PyPump",
        packages=["pypump"],
        license="GPLv3",
        install_requires=[
                "oauthlib-requests>=0.3.0",
                "requests>=1.2.0",
                ],
        classifiers=[
                "Development Status :: 3 - Alpha",
                "Programming Language :: Python",
                "Programming Language :: Python :: 2",
                "Programming Language :: Python :: 2.6",
                "Programming Language :: Python :: 2.7",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.3",
                "Programming Language :: Python :: Implementation :: CPython",
                "Operating System :: OS Independent",
                "Operating System :: POSIX",
                "Operating System :: Microsoft :: Windows",
                "Operating System :: MacOS :: MacOS X",
                "Operating System :: BeOS",
                "Intended Audience :: Developers",
                "License :: OSI Approved",
                "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
                ] 
     )
