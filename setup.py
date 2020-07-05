import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ds_create",
    version="0.1.4",
    author="Austin Poor",
    author_email="austinpoor@gmail.com",
    description="A simple CLI program for creating program templates.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/a-poor/ds-create",
    packages=setuptools.find_packages(),
    scripts=[
        "bin/ds-create"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
