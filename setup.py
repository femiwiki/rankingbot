import setuptools

setuptools.setup(
    name='rankingbot',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'mwclient',
    ],
)
