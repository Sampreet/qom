from setuptools import setup, find_packages

with open('README.md', 'r') as file_readme:
    long_desc = file_readme.read()

setup(
    name='qom-toolbox',
    version='0.6.0',
    author='Sampreet Kalita',
    author_email='sampreet.kalita@hotmail.com',
    desctiption='Quantum Optomechanics Toolbox',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    url='http://github.com/sampreet/qom',
    packages= find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering'
    ],
    license='MIT',
    install_requires=[
        'matplotlib>=3.0',
        'numpy>=1.10',
        'scipy>=1.0',
        'seaborn>=0.10',
        'setuptools>=40.0'
    ],
    python_requires='>=3.7',
    zip_safe=False
)
