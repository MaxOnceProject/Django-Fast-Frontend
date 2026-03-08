from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="django-fast-frontend",
    version="0.4.1",
    author="Blogbeat",
    author_email="support@blogbeat.app",
    description="Turbocharge Front-End Creation with Django-Admin-Like Configuration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MaxOnceProject/Django-Fast-Frontend",
    packages=find_packages(exclude=[
        'app', 'app.*',
        'app2', 'app2.*',
        'project', 'project.*',
    ]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
    ],
    python_requires='>=3.10',
    install_requires=[
        'django>=4.2',
        'django_bootstrap5>=26.2',
    ],
    include_package_data=True,
)
