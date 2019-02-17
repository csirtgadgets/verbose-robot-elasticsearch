import os
from setuptools import setup, find_packages
import versioneer
import sys

if sys.version_info < (3, 6):
    print("\n")
    print("This requires python 3.6 or higher")
    print("\n")
    raise SystemExit

# vagrant doesn't appreciate hard-linking
if os.environ.get('USER') == 'vagrant' or os.path.isdir('/vagrant'):
    del os.link

# https://www.pydanny.com/python-dot-py-tricks.html
if sys.argv[-1] == 'test':
    test_requirements = [
        'pytest',
        'coverage',
        'pytest_cov',
    ]
    try:
        modules = map(__import__, test_requirements)
    except ImportError as e:
        err_msg = e.message.replace("No module named ", "")
        msg = "%s is not installed. Install your test requirements." % err_msg
        raise ImportError(msg)
    r = os.system('py.test tests -sv --cov=cif_elasticsearch --cov-fail-under=30')
    if r == 0:
        sys.exit()
    else:
        raise RuntimeError('tests failed')

setup(
    name="cif_elasticsearch",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="CIFv4 ElasticSearch STore",
    long_description="",
    url="https://github.com/csirtgadgets/verbose-robot-elasticsearch",
    license='MPL2',
    classifiers=[
               "Topic :: System :: Networking",
               "Programming Language :: Python",
               ],
    keywords=['security'],
    author="Wes Young",
    author_email="wes@csirtgadgets.com",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        'verbose-robot',
        'elasticsearch-dsl'
    ],
    scripts=[],
    entry_points={
        'console_scripts': [
        ]
    },
)
