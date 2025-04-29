from setuptools import setup, find_packages

setup(
    name="auth_package",
    version="1.2.5",
    packages=find_packages(),
    install_requires=[
        "requests",
        "djangorestframework-simplejwt",
        "redis",
        "djangorestframework",
        "markdown",
        "django-filter",
        "grpcio",
        "grpcio-tools"
    ],
    description="A global authentication package for microservices",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Armin Fekri",
    author_email="armiin.fekri1@gmail.com",
    url="https://github.com/Hexoder/DjangoAuthService",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",  # Specify Python version compatibility
)



