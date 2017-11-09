from setuptools import find_packages
from setuptools import setup

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
        'keymint_package': [
            'template/dds/*',
            'template/keyage/*',
        ],
    },
)
