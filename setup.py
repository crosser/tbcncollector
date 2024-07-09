from setuptools import setup
from re import findall

with open("debian/changelog", "r") as clog:
    _, version, _ = findall(
        r"(?P<src>.*) \((?P<version>.*)\) (?P<suite>.*); .*",
        clog.readline().strip(),
    )[0]

setup(
    name="tbcncollector",
    version=version,
    description="Daemon to collect reports from ThermoBeacon devices",
    url="http://www.average.org/tbcncollector/",
    author="Eugene Crosser",
    author_email="crosser@average.org",
    install_requires=["bleak"],
    license="MIT",
    packages=[
        "tbcncollector",
    ],
    long_description=open("README.md").read(),
)
