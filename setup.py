import os.path
import setuptools

project_name = 'iterio-commons'
version = '0.1.0'

setup_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(setup_dir, 'README.rst')) as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name=project_name,
    version=version,
    description="Common code of Iterio's Python codebases.",
    long_description=readme,
    url=f'https://github.com/iteriodata/{project_name}',
    packages=setuptools.find_packages(exclude=['tests']),
    install_requires=['structlog'],
    license="MIT",
    keywords='iterio',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
    ],
    project_urls={
        'Bug Reports': f'https://github.com/iteriodata/{project_name}/issues',
        'Source': f'https://github.com/iteriodata/{project_name}',
    }
)
