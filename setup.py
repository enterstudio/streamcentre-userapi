from setuptools import setup

setup(
    name='StreamCentre UserAPI',
    version='0.1',
    long_description=__doc__,
    include_package_data=True,
    zip_safe=False,
    setup_requires=['Flask'],
    install_requires=['Flask', 'SQLAlchemy', 'Flask-Script', 'requests', 'HTTPretty']
)