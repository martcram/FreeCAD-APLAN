# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2015 Bernd Hahnebach <bernd@bimstatik.org>              *
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

__title__ = "ViewProvider for the FreeCAD APLAN PartFilter object"
__author__ = "Martijn Cramer, Bernd Hahnebach"
__url__ = "https://www.freecadweb.org"

## @package view_part_filter
#  \ingroup APLAN
#  \brief view provider for PartFilter object

from aplantools import aplanutils
try:
    from aplantaskpanels import task_part_filter
    import FreeCAD
    import FreeCADGui
    from pivy import coin
except ImportError as ie:
    aplanutils.missingPythonModule(str(ie.name or ""))


class ViewProviderPartFilter:
    """ViewProvider of the PartFilter object."""

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
        vobj.addDisplayMode(self.default,"Default")
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

    def getIcon(self):
        """
        Return the icon in XMP format which will appear in the tree view. This method is optional and if not defined a default icon is shown.
        """
        return ":/icons/APLAN_PartFilter.svg"

    def claimChildren(self):
        """
        Return a list of objects which will appear as children in the tree view.
        """
        return []

    def setEdit(self, vobj, mode=0):
        task = task_part_filter._TaskPanel(vobj.Object)
        FreeCADGui.Control.showDialog(task)
        return True

    def unsetEdit(self, vobj, mode=0):
        FreeCADGui.Control.closeDialog()
        return True
    
    def doubleClicked(self, vobj):
        guidoc = FreeCADGui.getDocument(vobj.Object.Document)
        # check if another VP is in edit mode
        # https://forum.freecadweb.org/viewtopic.php?t=13077#p104702
        if not guidoc.getInEdit():
            guidoc.setEdit(vobj.Object.Name)
        else:
            error: str = "Active Task Dialog found! Please close this one before opening a new one!"
            aplanutils.displayAplanError("Error in tree view", error)
            FreeCAD.Console.PrintError(error + "\n")
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
