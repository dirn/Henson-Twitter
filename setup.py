from setuptools import find_packages, setup

setup(
    name='Henson-Twitter',
    version='0.1.0',
    py_modules=['henson_twitter'],
    install_requires=[
        'aiohttp',
        'Henson',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development',
    ]
)
