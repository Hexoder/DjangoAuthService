from setuptools import setup, find_packages

setup(
    name="auth_package",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "djangorestframework-simplejwt",
        "redis",
        "djangorestframework",
        "markdown",
        "django-filter"
    ],
    description="A global authentication package for microservices",
    author="Armin Fekri",
    author_email="armiin.fekri1@gmail.com",
    url="https://github.com/Hexoder/cdn_package",
)
