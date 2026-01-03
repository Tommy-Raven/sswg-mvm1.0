#!/usr/bin/env python3

"""Package configuration for the AI Instructional Workflow Generator."""

from setuptools import setup, find_packages

setup(
    name="sswg-mvm",
    version="1.3.0+mvm",
    author="Tommy Byers (Tommy-Raven)",
    author_email="your.email@example.com",
    description="sswg mvm is the minimum viable model for the sswg workflow generation system.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Tommy-Raven/sswg-mvm1.0",
    packages=find_packages(
        include=[
            "ai_conductor",
            "ai_conductor.*",
            "ai_cores",
            "ai_cores.*",
            "ai_evaluation",
            "ai_evaluation.*",
            "ai_graph",
            "ai_graph.*",
            "ai_memory",
            "ai_memory.*",
            "ai_monitoring",
            "ai_monitoring.*",
            "ai_recursive",
            "ai_recursive.*",
            "ai_validation",
            "ai_validation.*",
            "ai_visualization",
            "ai_visualization.*",
            "cli",
            "cli.*",
            "data",
            "data.*",
            "generator",
            "generator.*",
            "modules",
            "modules.*",
            "meta_knowledge_repo",
            "meta_knowledge_repo.*",
            "config",
            "schemas",
        ]
    ),
    python_requires=">=3.10",
    install_requires=[
        "networkx>=3.2",
        "pyyaml>=6.0",
        "graphviz>=0.20.1",
        "jsonschema>=4.19",
        "sentence-transformers>=3.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0",
            "flake8>=7.0",
            "black>=24.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "sswg = cli.cli:main",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
