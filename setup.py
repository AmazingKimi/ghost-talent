from setuptools import find_packages, setup

setup(
    name="ghost-talent",
    version="0.2.0",
    description="Evidence-grounded discovery for emerging AI engineers and researchers",
    python_requires=">=3.10",
    packages=find_packages(include=["ghost_talent", "ghost_talent.*"]),
    install_requires=[
        "fastapi>=0.103,<0.104",
        "uvicorn[standard]>=0.23,<0.24",
        "httpx>=0.24,<0.25",
    ],
    entry_points={
        "console_scripts": [
            "ghost-talent=ghost_talent.app:main",
            "ghost-talent-watch=ghost_talent.watch:main",
            "ghost-talent-benchmark=ghost_talent.benchmark:main",
        ]
    },
)
