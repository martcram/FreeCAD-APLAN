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

__title__ = "Abstract base classes of the FreeCAD APLAN ObstructionDetector object"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

from aplantools import aplanutils
try:
    import abc
    import enum
    import FreeCAD
    import FreeCADGui
    from pivy import coin
    from PySide2 import QtCore, QtGui
    import typing
except ImportError as ie:
    aplanutils.missingPythonModule(str(ie.name or ""))


class IObstructionDetector(metaclass=abc.ABCMeta):
    BaseType = "Aplan::ObstructionDetectorPython"

    def __init__(self, obj):
        obj.Proxy = self
        if not hasattr(obj, "Type"):
            obj.addProperty(
                "App::PropertyString",
                "Type",
                "Obstruction detector",
                "Type of obstruction detector"
            )
            obj.setEditorMode("Type", 1)  # read-only

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class IVPObstructionDetector(metaclass=abc.ABCMeta):
    """ViewProvider of the ObstructionDetector object."""

    def __init__(self, vobj):
        """
        Set this object to the proxy object of the actual view provider
        """
        self.Object = vobj.Object
        vobj.Proxy = self

    def attach(self, vobj):
        """
        Setup the scene sub-graph of the view provider, this method is mandatory
        """
        self.default = coin.SoGroup()
        vobj.addDisplayMode(self.default, "Default")
        self.Object = vobj.Object

    def updateData(self, fp, prop):
        """
        If a property of the handled feature has changed we have the chance to handle this here
        """
        return

    def getDisplayModes(self, vobj):
        """
        Return a list of display modes.
        """
        return ["Default"]

    def getDefaultDisplayMode(self):
        """
        Return the name of the default display mode. It must be defined in getDisplayModes.
        """
        return "Default"

    def setDisplayMode(self, mode):
        """
        Map the display mode defined in attach with those defined in getDisplayModes.
        Since they have the same names nothing needs to be done.
        This method is optional.
        """
        return mode

    def onChanged(self, vp, prop):
        """
        Print the name of the property that has changed
        """
        return None

    def getIcon(self):
        """
        Return the icon in XMP format which will appear in the tree view. This method is optional and if not defined a default icon is shown.
        """
        return ":/icons/APLAN_ObstructionDetector.svg"

    def claimChildren(self):
        """
        Return a list of objects which will appear as children in the tree view.
        """
        return []

    def setEdit(self, vobj, mode=0):
        return True

    def unsetEdit(self, vobj, mode=0):
        return True

    def doubleClicked(self, vobj):
        return True

    def __getstate__(self):
        """
        Called during document saving.
        """
        return None

    def __setstate__(self, state):
        """
        Called during document restore.
        """
        return None


class ITaskPanel(metaclass=abc.ABCMeta):
    _COLOR_RUN:         typing.Final[str] = "yellowGreen"
    _COLOR_TERMINATING: typing.Final[str] = "darkOrange"
    _COLOR_ABORT:       typing.Final[str] = "crimson"
    
    def __init__(self, obstructionDetectorObject) -> None:
        self.obj = obstructionDetectorObject
        self._analysis = aplanutils.getActiveAnalysis()
        self._solverThread: typing.Optional[QtCore.QThread] = None
        self._solverType: typing.Final[str] = str(self.obj.Type)
        
        self.form = FreeCADGui.PySideUic.loadUi(
            FreeCAD.getHomePath() + 
            "Mod/Aplan/Resources/ui/aplan_obstruction_detectors/{}.ui"
            .format(self._solverType)
        )


class BaseWorker(QtCore.QObject):
    finished: QtCore.Signal = QtCore.Signal(dict)
    progress: QtCore.Signal = QtCore.Signal(dict)

    def __init__(self) -> None:
        super(BaseWorker, self).__init__()
        self._isRunning: bool = True

    def run(self) -> None:
        raise NotImplementedError

    def stop(self):
        self._isRunning = False

    @property
    def isRunning(self) -> bool:
        return self._isRunning


class MessageType(enum.Enum):
    FOCUS:   QtGui.QColor = QtGui.QColor(0, 0, 255)
    INFO:    QtGui.QColor = QtGui.QColor(0, 0, 0)
    WARNING: QtGui.QColor = QtGui.QColor(255, 140, 0)
    ERROR:   QtGui.QColor = QtGui.QColor(255, 0, 0)
