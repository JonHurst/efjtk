import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="efjtk",
    version="0.5",
    author="Jon Hurst",
    author_email="jon.a@hursts.org.uk",
    description="Convert EFJ files into FCL compliant logbooks and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JonHurst/efjtk",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        ("License :: OSI Approved :: "
         "GNU General Public License v3 or later (GPLv3+)"),
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
    install_requires=[
        "nightflight",
        "efj_parser"
    ],
    package_data={
        "efjtk": ["summary-template.html",
                        "logbook-template.html"]
    },
    entry_points={
        "console_scripts": ["efj = efjtk.cli:main"],
        "gui_scripts" : ["efjgui = efjtk.gui:main"]
    },
    project_urls = {
        "docs" : "https://hursts.org.uk/efjtkdocs/",
        },
)
