from setuptools import setup, Extension

with open("README.md") as f:
    long_descr = f.read()

setup(name='runmetal',
      version='0.1',
      description='run Apple Metal framework',
      long_description=long_descr,
      long_description_content_type="text/markdown",
      ext_modules=[
          Extension('mem', sources=['runmetal/memmodule.c']),
      ],
      author="Takashi WATANABE",
      author_email="wtnb75@gmail.com",
      url="https://github.com/wtnb75/runmetal",
      packages=["runmetal"],
      package_data={},
      license="MIT",
      install_requires=open("requirements.txt").readlines(),
      entry_points={
          "console_scripts": [
              "runmetal=runmetal.main:cli",
          ],
      },
      classifiers=[
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: MIT License",
          "Topic :: Software Development",
          "Programming Language :: Python :: 3",
      ],
      python_requires='>=3',
      keywords="apple metal gpu")
