#!/usr/bin/env python3

from setuptools import setup

setup(
    name="surveykit",
    version="0.1",
    description="SurveyKIT: tools for efficient work with SurveyCTO forms",
    author=u"Gabor Nyeki",
    url="https://www.gabornyeki.com/",
    packages=["surveykit"],
    install_requires=["argh", "xlrd"],
    provides=["surveykit (0.1)"],
    entry_points={
        "console_scripts": [
            "surveylint = surveykit.lint:dispatch",
        ],
    }
)
