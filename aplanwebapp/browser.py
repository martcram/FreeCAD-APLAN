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

__title__ = "FreeCAD APLAN browser view"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"


from aplantools import aplanutils
try:
    import FreeCADGui
    from PySide2 import QtCore, QtWebEngineWidgets, QtWidgets
except ImportError as ie:
    aplanutils.missingPythonModule(str(ie.name or ""))


# Source: along the lines of https://github.com/cadenasgmbh/3dfindit-freecad-integration

# Global variables
browserWidget = None
browser = None


class BrowserWidget(QtWidgets.QDockWidget):
    def __init__(self) -> None:
        super(BrowserWidget, self).__init__()

    def closeEvent(self, event):
        event.accept()


def createBrowserWidget():
    browserWidget = BrowserWidget()
    browserWidget.setObjectName("APLAN_BrowserWidget")
    browserWidget.setWidget(Dialog())

    FreeCADGui.getMainWindow().addDockWidget(
        QtCore.Qt.RightDockWidgetArea, browserWidget)

    return browserWidget


def getBrowser():
    global browser
    if browser is None:
        browser = Browser()
    return browser


def getBrowserWidget():
    global browserWidget
    if browserWidget is None:
        browserWidget = createBrowserWidget()
    return browserWidget


def isWidgetVisible() -> bool:
    return getBrowserWidget().toggleViewAction().isChecked()


def toggle():
    getBrowserWidget().toggleViewAction().trigger()


def show():
    if not isWidgetVisible():
        toggle()


def hide():
    if isWidgetVisible():
        toggle()


class Browser:
    def __init__(self):
        self._url: str = ""
        self._obj = None

        if browser is None:
            self._webView = QtWebEngineWidgets.QWebEngineView()
            self._webView.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        else:
            raise Exception("Invalid state.")

    @property
    def url(self):
        return self._url

    @property
    def webView(self):
        return self._webView

    def setUrl(self, url):
        self._url = url
        self._webView.setUrl(self._url)


class Dialog(QtWidgets.QDialog):
    def __init__(self):
        super(Dialog, self).__init__()

        # Setup the widget.
        self.setObjectName("APLAN_WebView_Dialog")
        self.setWindowTitle("APLAN webview dialog")

        # # Grab the browser.
        self.webView = getBrowser().webView

        # # Prepare a simple layout.
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(QtWidgets.QHBoxLayout())
        self.layout.addWidget(self.webView)

    def showEvent(self, event):
        super(Dialog, self).showEvent(event)

    def hideEvent(self, event):
        super(Dialog, self).hideEvent(event)

    def event(self, event):
        if event.type() == QtCore.QEvent.ShortcutOverride:
            event.accept()
        return super(Dialog, self).event(event)
