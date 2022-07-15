# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2022 Martijn Cramer <martijn.cramer@outlook.com>        *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "APLAN Utilities"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

import FreeCAD
import ObjectsAplan
if FreeCAD.GuiUp:
    import FreeCADGui
    import AplanGui
    try:
        from PySide2 import QtWidgets
    except ImportError as ie:
        print("Missing dependency! Please install the following Python module: {}".format(str(ie.name or "")))
try:
    import typing
    import xml.etree.ElementTree as ET
except ImportError as ie:
    print("Missing dependency! Please install the following Python module: {}".format(str(ie.name or ""))) 


# Source: src/Mod/Fem/femtools/femutils.py
def createObject(doc, name: str, proxy, viewProxy = None):
    """Add Python object to document using Python type string.

    Add a document object suitable for the *proxy* and the *viewProxy* to *doc*
    and attach it to the *proxy* and the *viewProxy*. This function can only be
    used with Python proxies that specify their C++ type via the BaseType class
    member (e.g. Cube.BaseType). If there already exists a object with *name* a
    suitable unique name is generated. To auto generate a name pass ``""``.

    :param doc:         document object to which the object is added
    :param name:        string of the name of new object in *doc*, use
                        ``""`` to generate a name
    :param proxy:       Python proxy for new object
    :param viewProxy:   view proxy for new object

    :returns:           reference to new object
    """
    obj = doc.addObject(proxy.BaseType, name)
    proxy(obj)
    if FreeCAD.GuiUp and viewProxy is not None:
        viewProxy(obj.ViewObject)
    return obj


def displayAplanError(message: str, error: str) -> None:
    """Displays a QMessageBox for notifying errors related to the APLAN workbench.

    :param message: brief error message to display
    :type message: str
    :param error: detailed description of the error and the potential solution
    :type error: str
    """
    QtWidgets.QMessageBox.critical(FreeCADGui.getMainWindow(), "APLAN ERROR",
    "{}\n\nError: {}".format(message, error))


def getActiveAnalysis():
    """Returns the active analysis in the current document.

    :return: the active analysis object if present
    :rtype: `AplanAnalysis` or `None`
    """
    analysis = AplanGui.getActiveAnalysis()
    if analysis.Document is FreeCAD.ActiveDocument:
        return analysis
    return None


def getCompoundGroup(analysis):
    """Returns the first CompoundGroup of the corresponding analysis.
    If no CompoundGroup is present, one will be added to the analysis.

    :param analysis: the analysis object
    :type analysis: `AplanAnalysis`
    :return: the compound group object
    :rtype: `AplanCompoundGroup`
    """
    groupObjects = analysis.CompoundGroupObjects
    if not groupObjects:
        compoundGroup = ObjectsAplan.makeCompoundGroup(FreeCAD.ActiveDocument)
        analysis.addObject(compoundGroup)
        return compoundGroup
    else:
        return groupObjects[0]


def getConstraintGroup(analysis): # if no constraints container is present, one will be created
    """Returns the first ConstraintGroup of the corresponding analysis.
    If no ConstraintGroup is present, one will be added to the analysis.

    :param analysis: the analysis object
    :type analysis: `AplanAnalysis`
    :return: the constraint group object
    :rtype: `AplanConstraintGroup`
    """
    groupObjects = analysis.ConstraintGroupObjects
    if not groupObjects:
        constraintGroup = ObjectsAplan.makeConstraintGroup(FreeCAD.ActiveDocument)
        analysis.addObject(constraintGroup)
        return constraintGroup
    else:
        return groupObjects[0]


def getPropertyEnumerationValues(object, propertyName: str) -> typing.List[str]:
    """Returns the list of possible values of the object's specified `PropertyEnumeration` property.

    :param object: FreeCAD object
    :type object: `FeaturePython`
    :param propertyName: name of the enumeration property to retreive the values from
    :type propertyName: str
    :return: list of the enumeration property's values
    :rtype: typing.List[str]
    """
    propertiesElement: ET.Element = ET.fromstring(object.Content)
    propertyElements: typing.List[ET.Element] = propertiesElement.findall("Property")
    enumValues: typing.List = []
    if propertyElement := next(iter(p for p in propertyElements 
                                    if p.get("name") == propertyName and 
                                       p.get("type") == "App::PropertyEnumeration"), None):
        enumValues = list(map(lambda e: e.get("value"), propertyElement.iter("Enum")))
    return enumValues


def missingPythonModule(name: str) -> None:
    """Displays a QMessageBox stating that a dependency is missing and 
    asking the user to install the absent Python module.

    :param name: name of the missing Python module
    :type name: str
    """
    QtWidgets.QMessageBox.critical(FreeCADGui.getMainWindow(), 
        "Missing dependency", "Please install the following Python module: {}".format(name))


def purgeCompounds(analysis) -> None:
    """Removes all Compound and CompoundGroup objects of the specified analysis.

    :param analysis: the analysis object
    :type analysis: `AplanAnalysis`
    """
    for group in analysis.CompoundGroupObjects:
        for compound in group.Group:
            analysis.Document.removeObject(compound.Name)
        analysis.Document.removeObject(group.Name)
    analysis.Document.recompute()


def purgeConstraints(analysis):
    """Removes all ConstraintGroup objects and their constraints of the specified analysis.

    :param analysis: the analysis object
    :type analysis: `AplanAnalysis`
    """
    for group in analysis.ConstraintGroupObjects:
        for obj in group.Group:
            analysis.Document.removeObject(obj.Name)
        analysis.Document.removeObject(group.Name)
    analysis.Document.recompute()
