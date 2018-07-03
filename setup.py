import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mycorrhiza",
    version="0.0.1",
    author="Jeremy Georges-Filteau",
    author_email="jeremy.georges-filteau@mail.mcgill.ca",
    description="Mycorrhiza population assignment tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jgeofil/mycorrhiza",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "LICENSE :: OSI APPROVED :: GNU GENERAL PUBLIC LICENSE V3 (GPLV3)Close",
        "Operating System :: OS Independent",
    ),
)