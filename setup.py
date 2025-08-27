from setuptools import setup, find_packages

setup(
    name='linkmap',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'requests',
        'beautifulsoup4',
        'SQLAlchemy',
        'Jinja2',
        'lxml',
    ],
    entry_points={
        'console_scripts': [
            'linkmap = linkmap.cli:cli',
        ],
    },
)
