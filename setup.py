from setuptools import setup, find_packages

with open('README.md', 'r') as file_readme:
    long_desc = file_readme.read()

setup(
    name='qom',
    version='0.7.6',
    author='Sampreet Kalita',
    author_email='sampreet.kalita@hotmail.com',
    desctiption='The Quantum Optomechanics Toolbox',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    keywords=['quantum', 'optomechanics', 'toolbox', 'python3'],
    url='https://github.com/sampreet/qom',
    download_url='https://github.com/Sampreet/qom/archive/refs/tags/v0.7.5.tar.gz',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering'
    ],
    license='BSD',
    install_requires=[
        'matplotlib>=3.3',
        'numpy>=1.19',
        'pyqt5>=5.9',
        'scipy>=1.5',
        'seaborn>=0.11',
        'sympy>=1.6'
    ],
    python_requires='>=3.8',
    zip_safe=False,
    include_package_data=True
)
