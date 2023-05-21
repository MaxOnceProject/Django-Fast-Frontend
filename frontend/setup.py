from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="django-fast-frontend",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A fast and efficient frontend for Django projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/django-fast-frontend",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
    ],
    python_requires='>=3.6',
    install_requires=[
        'django>=3.0,<4.0',
        # other dependencies...
    ],
    include_package_data=True,
)
