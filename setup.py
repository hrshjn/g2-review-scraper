from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="g2-review-scraper",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to scrape reviews from G2.com using Google Gemini AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/g2-review-scraper",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.32.0",
        "google-generativeai>=0.8.0",
        "pandas>=2.0.0",
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "g2scraper=scraper:main",
        ],
    },
) 