from setuptools import setup, find_packages

with open("../README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="django-fast-frontend",
    version="0.1.0",
    author="Blogbeat",
    author_email="support@blogbeat.app",
    description="Turbocharge Front-End Creation with Django-Admin-Like Configuration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MaxOnceProject/Django-Fast-Frontend",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
    ],
    python_requires='>=3.8',
    install_requires=[
        'django>=4.0',
        'django_bootstrap5>=21.1',
        # other dependencies...
    ],
    include_package_data=True,
)
