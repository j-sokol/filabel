from setuptools import setup, find_packages


with open('README.md') as f:
    long_description = ''.join(f.readlines())


setup(
    name='filabel_sokolja2',
    version='0.3.1.1',
    description='Tool for labeling PRs at GitHub by globs.',
    long_description=long_description,
    author='Jan Sokol',
    author_email='sokolja2@fit.cvut.cz',
    keywords='label,github,git,flask,cli,web',
    license='Public Domain',
    url='https://github.com/j-sokol/filabel',
    # packages=['filabel'],
    packages=find_packages(),
    install_requires=[
        'Flask',
        'click>=6',
        'gunicorn>=19',
        'requests',
        'pytest'
        ],
    entry_points={
        'console_scripts': [
            'filabel = filabel.cli.filabel:cli',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Framework :: Flask',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
        'Natural Language :: English',
        'Topic :: Software Development :: Version Control :: Git',
        'Environment :: Console',
        'Environment :: Web Environment'

        ],
    zip_safe=False,
)