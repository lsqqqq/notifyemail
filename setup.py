from distutils.core import setup

from setuptools import find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(name='notifyemail', # 包名
      version='1.0.2', # 版本号
      description='python邮件小工具',

      long_description=long_description,
      long_description_content_type="text/markdown",
      author='LvShangqing, ZhangTianyi, LeiYanli',

      author_email='seblei@163.com',

      url='https://github.com/lsqqqq/notify',

      install_requires=[],
      license='BSD License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries'
    ],

)
