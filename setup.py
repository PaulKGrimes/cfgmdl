from setuptools import setup

from python.cfgmdl.version import get_git_version

setup(
    name="cfgmdl",
    version=get_git_version(),
    author="",
    author_email="",
    url = "https://github.com/KIPAC/cfgmdl",
    package_dir={"":"python"},
    packages=["cfgmdl"],
    description="=Tools for configuration parsing and model building",
    long_description=open("README.md").read(),
    package_data={"": ["README.md", "LICENSE"]},
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        ],
    install_requires=["numpy", "jax", "jaxlib", "pyyaml"],
    python_requires='>=3.7',
)
