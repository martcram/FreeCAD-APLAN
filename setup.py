from setuptools import setup
from freecad.aplan_workbench.version import __version__

setup(
    name="freecad.aplan_workbench",
    version=str(__version__),
    description="Assembly PLANning workbench for FreeCAD",
    packages=['freecad',
              'freecad.aplan_workbench'],
    maintainer="martcram",
    maintainer_email="martijn.cramer@kuleuven.be",
    url="https://github.com/martcram/FreeCAD-APLAN",
    install_requires=["matplotlib", "networkx", "numpy"],
    python_requires=">=3",
    include_package_data=True
)