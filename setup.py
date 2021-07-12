import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyoocass", 
    version="0.0.2",
    author="Jesus Alejandro Sanchez Davila",
    author_email="jsanchez.consultant@gmail.com",
    description="Python Object-Orinted Cassandra interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Silvarion/pyoocass",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'cassandra-driver',
        'time_uuid',
        'uuid'
    ]
)
