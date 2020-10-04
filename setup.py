#!/usr/bin/env python3

from setuptools import setup


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="honeybee",
    version="0.2010041859",
    description="Honeybee: tools for efficient editing of XLSForm questionnaires",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=u"Gabor Nyeki",
    url="https://www.gabornyeki.com/",
    packages=[
        "honeybee",
        "honeybee.comb_to_xlsform"
    ],
    install_requires=["argh", "pyparsing", "openpyxl"],
    entry_points={
        "console_scripts": [
            "beepile = honeybee.comb_to_xlsform:dispatch",
            "beelint = honeybee.lint:dispatch",
        ],
    },
    python_requires=">=3.0"
)
