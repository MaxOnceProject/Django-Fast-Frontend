import os


def pytest_configure(config):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
