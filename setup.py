from setuptools import setup

setup(
    name="fancycompleter",
    setup_requires=["setuptools_scm"],
    version_file="fancycompleter/_version.py",
    use_scm_version=True,
    versioning="devcommit",
    maintainer="Daniel Hahler",
    url="https://github.com/pdbpp/fancycompleter",
    packages=["fancycompleter"],
    author="Antonio Cuni",
    author_email="anto.cuni@gmail.com",
    license="BSD",
    description="colorful TAB completion for Python prompt",
    keywords="rlcompleter prompt tab color completion",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Utilities",
    ],
    install_requires=[
        "pyrepl @ git+https://github.com/bretello/pyrepl@0.10.0",
        "pyreadline;platform_system=='Windows'",
    ],
)
