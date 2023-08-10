/***************************************************************************
 *                                                                         *
 *   Copyright (c) 2013 Jürgen Riegel <FreeCAD@juergen-riegel.net>         *
 *   Copyright (c) 2022 Martijn Cramer <martijn.cramer@outlook.com>        *
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

#ifndef _PreComp_
#include <QAction>
#include <QMenu>
#endif

#include <Gui/ActionFunction.h>
#include <Gui/Command.h>
#include <Gui/Control.h>
#include <Gui/TaskView/TaskDialog.h>
#include <Gui/ViewProvider.h>
#include <Gui/ViewProviderDocumentObjectGroup.h>

#include <Mod/Aplan/App/AplanAnalysis.hpp>
#include <Mod/Aplan/Gui/TaskAplanAnalysis.hpp>
#include <Mod/Aplan/Gui/ViewProviderAnalysis.hpp>

using namespace AplanGui;

/* TRANSLATOR AplanGui::ViewProviderAplanAnalysis */

PROPERTY_SOURCE(AplanGui::ViewProviderAplanAnalysis, Gui::ViewProviderDocumentObjectGroup)

ViewProviderAplanAnalysis::ViewProviderAplanAnalysis()
{
    sPixmap = "APLAN_Analysis";
}

ViewProviderAplanAnalysis::~ViewProviderAplanAnalysis()
{
}

bool ViewProviderAplanAnalysis::doubleClicked(void)
{
    this->setEdit(ViewProvider::Default);
    Gui::Command::assureWorkbench("AplanWorkbench");
    Gui::Command::addModule(Gui::Command::Gui, "AplanGui");
    Gui::Command::doCommand(Gui::Command::Gui, "AplanGui.setActiveAnalysis(App.activeDocument().%s)", this->getObject()->getNameInDocument());
    return true;
}

std::vector<App::DocumentObject *> ViewProviderAplanAnalysis::claimChildren(void) const
{
    return Gui::ViewProviderDocumentObjectGroup::claimChildren();
}

bool ViewProviderAplanAnalysis::canDelete(App::DocumentObject *obj) const
{
    Q_UNUSED(obj)
    return true;
}

std::vector<std::string> ViewProviderAplanAnalysis::getDisplayModes(void) const
{
    return {"Analysis"};
}

void ViewProviderAplanAnalysis::hide(void)
{
    Gui::ViewProviderDocumentObjectGroup::hide();
}

void ViewProviderAplanAnalysis::show(void)
{
    Gui::ViewProviderDocumentObjectGroup::show();
}

void ViewProviderAplanAnalysis::setupContextMenu(QMenu *menu, QObject *, const char *)
{
    Gui::ActionFunction *func = new Gui::ActionFunction(menu);
    QAction *act = menu->addAction(tr("Activate analysis"));
    func->trigger(act, boost::bind(&ViewProviderAplanAnalysis::doubleClicked, this));
}

bool ViewProviderAplanAnalysis::setEdit(int ModNum)
{
    if (ModNum == ViewProvider::Default)
    {
        // Base::Console().Message("\n");
        Gui::TaskView::TaskDialog *dlg = Gui::Control().activeDialog();
        TaskDlgAplanAnalysis *analysisDlg = qobject_cast<TaskDlgAplanAnalysis *>(dlg);
        if (analysisDlg && analysisDlg->getAnalysisView() != this)
            analysisDlg = 0; // another Analysis left open its task panel

        // clear the selection (convenience)
        Gui::Selection().clearSelection();

        // start the edit dialog
        if (analysisDlg)
        {
            Gui::Control().showDialog(analysisDlg);
        }
        else
        {
            Gui::Control().showDialog(new TaskDlgAplanAnalysis(this));
        }
        return false;
    }
    else
    {
        return Gui::ViewProviderDocumentObjectGroup::setEdit(ModNum);
    }
}

void ViewProviderAplanAnalysis::unsetEdit(int ModNum)
{
    if (ModNum == ViewProvider::Default)
    {
        // when pressing ESC make sure to close the dialog
        Gui::Control().closeDialog();
    }
    else
    {
        Gui::ViewProviderDocumentObjectGroup::unsetEdit(ModNum);
    }
}

bool ViewProviderAplanAnalysis::onDelete(const std::vector<std::string> &)
{
    return true;
}

bool ViewProviderAplanAnalysis::canDragObjects() const
{
    return true;
}

bool ViewProviderAplanAnalysis::canDragObject(App::DocumentObject *obj) const
{
    if (!obj)
        return false;
    else if (obj->getTypeId().isDerivedFrom(Base::Type::fromName("Aplan::FeaturePython")))
        return true;
    else
        return false;
}

void ViewProviderAplanAnalysis::dragObject(App::DocumentObject *obj)
{
    ViewProviderDocumentObjectGroup::dragObject(obj);
}

bool ViewProviderAplanAnalysis::canDropObjects() const
{
    return true;
}

bool ViewProviderAplanAnalysis::canDropObject(App::DocumentObject *obj) const
{
    return canDragObject(obj);
}

void ViewProviderAplanAnalysis::dropObject(App::DocumentObject *obj)
{
    ViewProviderDocumentObjectGroup::dropObject(obj);
}

// Python feature -----------------------------------------------------------------------

namespace Gui
{
    /// @cond DOXERR
    PROPERTY_SOURCE_TEMPLATE(AplanGui::ViewProviderAplanAnalysisPython, AplanGui::ViewProviderAplanAnalysis)
    /// @endcond

    // explicit template instantiation
    template class AplanGuiExport ViewProviderPythonFeatureT<ViewProviderAplanAnalysis>;
}
