# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="neurohr",
    version="0.1.0",
    description="Система для проведения собеседований с использованием нейросетей",
    author="Ваше имя",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "langchain>=0.0.335",
        "langchain-community>=0.0.35",
        "langchain-openai>=0.0.5",
        "langchain-core>=0.1.15",
        "faiss-cpu>=1.7.4",
        "rarfile>=4.0",
        "PyPDF2>=3.0.0",
        "pydub>=0.25.1",
        "gtts>=2.5.0",
        "ipywidgets>=8.0.0",
        "requests>=2.28.0",
        "tqdm>=4.66.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "neurohr=neurohr.main:main",
        ],
    },
)
