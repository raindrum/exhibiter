import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="exhibiter",
    version="1.0",
    description="a tool to organize evidence for litigation",
    author="Simon Raindrum Sherred",
    author_email="simonraindrum@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raindrum/exhibiter",
    packages=setuptools.find_packages(),
    scripts=['exhibiter/exhibiter.py'],
    install_requires=[
        'img2pdf',
        'pdfrw',
        'texttable',
        'pypandoc',
        'pillow',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: DON'T EVICT",
        "Operating System :: OS Independent",
    ],
    python_require='>=3.8',
)
