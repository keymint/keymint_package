import os

from setuptools import find_packages
from setuptools import setup


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


extra_files = []
extra_files.extend(package_files('keymint_package/schema'))
extra_files.extend(package_files('keymint_package/template'))


setup(
    name='keymint_package',
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    author='Ruffin White',
    author_email='ruffin@osrfoundation.org',
    maintainer='Ruffin White',
    maintainer_email='ruffin@osrfoundation.org',
    url='https://github.com/keymint/keymint_package/wiki',
    download_url='https://github.com/keymint/keymint_package/releases',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description='Keymint is a build system for keystores.',
    long_description="""\
Keymint defines metainformation for keys, their certificats,
and provides tooling to build these federated keystores together.""",
    license='Apache License, Version 2.0',
    test_suite='test',
    package_data={
        'keymint_package': extra_files,
    },
)
