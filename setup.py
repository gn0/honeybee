#!/usr/bin/env python3

from setuptools import setup

setup(
    name="honeybee",
    version="0.1",
    description="Honeybee: tools for efficient editing of XLSForm questionnaires",
    author=u"Gabor Nyeki",
    url="https://www.gabornyeki.com/",
    packages=[
        "honeybee",
        "honeybee.comb_to_xlsform"
    ],
    install_requires=["argh", "xlrd"],
    provides=["honeybee (0.1)"],
    entry_points={
        "console_scripts": [
            "beepile = honeybee.comb_to_xlsform:dispatch",
            "beelint = honeybee.lint:dispatch",
        ],
    }
)
