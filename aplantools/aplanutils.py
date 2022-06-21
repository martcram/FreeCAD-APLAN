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

import FreeCADGui
from PySide2 import QtWidgets


def missingPythonModule(name: str) -> None:
    """Displays a QMessageBox stating that a dependency is missing and 
    asking the user to install the absent Python module.

    :param name: name of the missing Python module
    :type name: str
    """
    QtWidgets.QMessageBox.critical(FreeCADGui.getMainWindow(), 
        "Missing dependency", "Please install the following Python module: {}".format(name))
