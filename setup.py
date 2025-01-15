import io
import os

from setuptools import setup

from huskium.version import VERSION


LONG_DESCRIPTION = io.open(
    os.path.join(os.path.dirname(__file__), 'README.md'),
    encoding='utf-8'
).read()


setup(
    name='huskium',
    version=VERSION,
    description='UI Automation Page Objects design pattern.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Johnny',
    author_email='johnny071531@gmail.com',
    url='https://github.com/uujohnnyuu/huskium',
    license='Apache 2.0',
    keywords=['huskium', 'huskypo', 'selenium', 'appium', 'page object', 'automation'],
    packages=["huskium"],
    install_requires=['Appium-Python-Client >= 4.0.0'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.11',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
    ]
)
