from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(
    name="smart_delta",
    version="1.0.0",
    packages=find_packages(exclude=["tests*"]),
    description="Tool for creating string deltas between strings.",
    long_description=open("README.md").read(),
    url="https://github.com/JesusDMan/BackupSyncer",
    author="JesusDMan",
    install_requires=["cython"],
    ext_modules=cythonize("smart_delta/src/delta_utils.py"),
    entry_points={
        "console_scripts": [
            "delta-gen = smart_delta.bin.create_delta:main",
            "delta-apply = smart_delta.bin.apply_delta:main",
        ]
    },
)
