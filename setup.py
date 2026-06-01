from setuptools import find_packages, setup


setup(
    name="diffdocket",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages("src"),
    entry_points={"console_scripts": ["diffdocket=pr_review_receipt.cli:main"]},
    extras_require={"dev": ["pytest>=8.0"]},
    python_requires=">=3.11",
)
