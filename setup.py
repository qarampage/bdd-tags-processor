from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="bdd_tags_processor",
    version="0.1.0",
    description="Filter Feature-Files based on Scenario Tag expressions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="QA Rampage",
    author_email="16265665+qarampage@users.noreply.github.co",
    url="https://github.com/qarampage/bdd-tags-processor",
    packages=find_packages(),
    install_requires=[],
    keywords="bdd cucumber tag expression processor filter feature files",
    classifiers=[
        "License :: OSI Approved :: GNU GENERAL PUBLIC LICENSE",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={
        "console_scripts": [
            "bdd_tags_processor=bdd_tags_processor.bdd_tags_expression_processor:main",
        ],
    }
)