import setuptools

setuptools.setup(
    name='store_monitoring',
    version='1.0.0',
    author='Lav Sharma',
    author_email='lavsharma2016@gmail.com',
    description='Store monitoring system',
    long_description='',
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    install_requires=['uvicorn>=0.16.0', 'fastapi>=0.83.0', 'configparser>=6.0.0', 'requests>=2.31.0',
                      'retrying>=1.3.4', 'pandas>=2.1.2']
)
