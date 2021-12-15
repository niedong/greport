from setuptools import setup, find_packages

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name='greport',
    version='0.1.8',
    description='Generate html from googletest xml file',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='niedong',
    author_email='niedong0816@126.com',
    url='https://github.com/niedong/greport',
    install_requires=["jinja2"],
    packages=find_packages(),
    package_data={'greport': ['template.html']},
    include_package_data=True,
    entry_points={'console_scripts': ["greport=greport.__main__:main"]},
)
