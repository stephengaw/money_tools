from setuptools import setup, find_packages


with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name='money_tools',
    version='0.1dev',
    packages=find_packages(exclude=["*.tests"]),
    license='asdsadf',
    long_description='Money Tools',
    install_requires=REQUIREMENTS,
    setup_requires=["pytest-runner"],
    tests_require=["pytest"]
)
