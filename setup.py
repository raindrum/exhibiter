import setuptools

with open('README.md', 'r') as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name='exhibiter',
    version='1.0.1',
    description='a tool to organize evidence for litigation',
    author='Simon Raindrum Sherred',
    author_email='simonraindrum@gmail.com',
    license="Non-Eviction",
    long_description=readme,
    long_description_content_type="text/markdown",
    url='https://github.com/raindrum/exhibiter',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ["exhibiter-cli = exhibiter.cli:cli"],
        'gui_scripts': ["exhibiter = exhibiter.gui:gui"]},
    include_package_data=True,
    install_requires=[
        'pdfrw',
        'pillow',
        'reportlab',
        'python-docx',
        'PySide2'],
    classifiers=[
        'License :: Free To Use But Restricted',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Legal Industry',
        'Programming Language :: Python :: 3.8',
        'Environment :: Console',
        'Environment :: Other Environment',
        'Operating System :: OS Independent'],
    python_require='>=3.8',
)
