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
import FreeCADGui
from PySide2 import QtWidgets


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


def missingPythonModule(name: str) -> None:
    """Displays a QMessageBox stating that a dependency is missing and 
    asking the user to install the absent Python module.

    :param name: name of the missing Python module
    :type name: str
    """
    QtWidgets.QMessageBox.critical(FreeCADGui.getMainWindow(), 
        "Missing dependency", "Please install the following Python module: {}".format(name))
