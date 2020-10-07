import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='exhibiter',
    version='0.10.0',
    description='a tool to organize evidence for litigation',
    author='Simon Raindrum Sherred',
    author_email='simonraindrum@gmail.com',
    license="Non-Eviction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/raindrum/exhibiter',
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "exhibiter = exhibiter.exhibiter:cli_launch",
        ]
    },
    include_package_data=True,
    install_requires=[
        'img2pdf',
        'pdfrw',
        'texttable',
        'pypandoc',
        'pillow',
        'reportlab'
    ],
    classifiers=[
        'License :: Free To Use But Restricted',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Legal Industry',
        'Programming Language :: Python :: 3.8',
        'Environment :: Console',
        'Environment :: Other Environment',
        'Operating System :: OS Independent',
    ],
    python_require='>=3.8',
)
