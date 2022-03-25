from pathlib import Path

from setuptools import find_packages, setup

long_description = Path('README.md').read_text(encoding='utf-8')


def load_requirements(filename):
    with Path(filename).open() as f:
        return [line.strip() for line in f if not line.startswith('#')]


__version__ = None
with open('onepush/__version__.py', encoding='utf-8') as f:
    exec(f.read())

if not __version__:
    print('Could not find __version__ from onepush/__version__.py')
    exit(-1)

setup(
    name='onepush',
    version=__version__,
    packages=find_packages(),
    url='https://github.com/y1ndan/onepush',
    license='MIT',
    author='y1ndan',
    author_email='y1nd4n@outlook.com',
    description='A Python library to send notifications to your iPhone, Discord, Telegram, WeChat, QQ and DingTalk.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='notify notifier notification push discord telegram wechat qq dingtalk',
    include_package_data=True,
    install_requires=load_requirements('requirements.txt'),
    tests_require=['pytest'],
    classifiers=[
        # As from https://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.3',
        # 'Programming Language :: Python :: 2.4',
        # 'Programming Language :: Python :: 2.5',
        # 'Programming Language :: Python :: 2.6',
        # 'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.0',
        # 'Programming Language :: Python :: 3.1',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Systems Administration',
    ],
    python_requires='>=3.6',
)
