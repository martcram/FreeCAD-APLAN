/***************************************************************************
 *                                                                         *
 *   Copyright (c) 2013 Werner Mayer <wmayer[at]users.sourceforge.net>     *
 *   Copyright (c) 2021 Martijn Cramer <martijn.cramer@outlook.com>        *
 *                                                                         *
 *   This file is part of the FreeCAD CAx development system.              *
 *                                                                         *
 *   This library is free software; you can redistribute it and/or         *
 *   modify it under the terms of the GNU Library General Public           *
 *   License as published by the Free Software Foundation; either          *
 *   version 2 of the License, or (at your option) any later version.      *
 *                                                                         *
 *   This library  is distributed in the hope that it will be useful,      *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU Library General Public License for more details.                  *
 *                                                                         *
 *   You should have received a copy of the GNU Library General Public     *
 *   License along with this library; see the file COPYING.LIB. If not,    *
 *   write to the Free Software Foundation, Inc., 59 Temple Place,         *
 *   Suite 330, Boston, MA  02111-1307, USA                                *
 *                                                                         *
 ***************************************************************************/

#include "PreCompiled.hpp"

#include <Gui/Application.h>
#include <Gui/Document.h>
#include <Gui/ViewProviderDocumentObject.h>

#include <Mod/Aplan/App/AplanAnalysis.hpp>
#include "ActiveAnalysisObserver.hpp"

using namespace AplanGui;

ActiveAnalysisObserver *ActiveAnalysisObserver::inst = 0;

ActiveAnalysisObserver *ActiveAnalysisObserver::instance()
{
    if (!inst)
        inst = new ActiveAnalysisObserver();
    return inst;
}

ActiveAnalysisObserver::ActiveAnalysisObserver()
    : activeObject(0), activeView(0), activeDocument(0), highlightMode(Gui::HighlightMode::UserDefined)
{
    // Set required parameters for HighlightMode::UserDefined
    ParameterGrp::handle treeViewGrp = App::GetApplication().GetParameterGroupByPath("User parameter:BaseApp/Preferences/TreeView");
    treeViewGrp->SetBool("TreeActiveBold", false);
    treeViewGrp->SetBool("TreeActiveItalic", false);
    treeViewGrp->SetBool("TreeActiveUnderlined", false);
    treeViewGrp->SetBool("TreeActiveOverlined", false);
    treeViewGrp->SetUnsigned("TreeActiveColor", 4290607871);
}

ActiveAnalysisObserver::~ActiveAnalysisObserver()
{
}

void ActiveAnalysisObserver::setActiveObject(Aplan::AplanAnalysis *aplan)
{
    if (aplan)
    {
        activeObject = aplan;
        App::Document *doc = aplan->getDocument();
        activeDocument = Gui::Application::Instance->getDocument(doc);
        activeView = static_cast<Gui::ViewProviderDocumentObject *>(activeDocument->getViewProvider(activeObject));
        attachDocument(doc);
    }
    else
    {
        activeObject = 0;
        activeView = 0;
    }
}

Aplan::AplanAnalysis *ActiveAnalysisObserver::getActiveObject() const
{
    return activeObject;
}

bool ActiveAnalysisObserver::hasActiveObject() const
{
    return activeObject != 0;
}

void ActiveAnalysisObserver::highlightActiveObject(const Gui::HighlightMode &mode, bool on)
{
    if (activeDocument && activeView)
    {
        activeDocument->signalHighlightObject(*activeView, mode, on, 0, 0);
        this->highlightMode = mode;
    }
}

void ActiveAnalysisObserver::unsetActiveObject()
{
    if (this->hasActiveObject())
    {
        this->highlightActiveObject(this->highlightMode, false);
        this->setActiveObject(0);
    }
}

void ActiveAnalysisObserver::slotDeletedDocument(const App::Document &Doc)
{
    App::Document *d = getDocument();
    if (d == &Doc)
    {
        activeObject = 0;
        activeDocument = 0;
        activeView = 0;
        detachDocument();
    }
}

void ActiveAnalysisObserver::slotDeletedObject(const App::DocumentObject &Obj)
{
    if (activeObject == &Obj)
    {
        activeObject = 0;
        activeView = 0;
    }
}
