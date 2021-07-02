import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="edgex-taf-common",
    description="EdgeX Test Automation Framework Common ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/edgexfoundry/edgex-taf-common",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    license='Apache License'
)
