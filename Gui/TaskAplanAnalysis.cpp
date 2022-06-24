/******************************************************************************
 *                                                                            *
 *   Copyright (c) 2013 Jan Rheinländer <jrheinlaender@users.sourceforge.net> *
 *   Copyright (c) 2022 Martijn Cramer <martijn.cramer@outlook.com>           *
 *                                                                            *
 *   This file is part of the FreeCAD CAx development system.                 *
 *                                                                            *
 *   This library is free software; you can redistribute it and/or            *
 *   modify it under the terms of the GNU Library General Public              *
 *   License as published by the Free Software Foundation; either             *
 *   version 2 of the License, or (at your option) any later version.         *
 *                                                                            *
 *   This library  is distributed in the hope that it will be useful,         *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of           *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            *
 *   GNU Library General Public License for more details.                     *
 *                                                                            *
 *   You should have received a copy of the GNU Library General Public        *
 *   License along with this library; see the file COPYING.LIB. If not,       *
 *   write to the Free Software Foundation, Inc., 59 Temple Place,            *
 *   Suite 330, Boston, MA  02111-1307, USA                                   *
 *                                                                            *
 ******************************************************************************/

#include "PreCompiled.hpp"

#include <Gui/BitmapFactory.h>
#include <Gui/Command.h>
#include <Gui/MainWindow.h>
#include <Gui/TaskView/TaskDialog.h>

#include <QDir>
#include <QFileDialog>
#include <QMessageBox>
#include <QObject>
#include <QWidget>

#include <Mod/Aplan/App/AplanAnalysis.hpp>
#include <Mod/Aplan/Gui/TaskAplanAnalysis.hpp>
#include "ui_TaskAplanAnalysis.h"

using namespace AplanGui;
using namespace Gui;

TaskAplanAnalysis::TaskAplanAnalysis(ViewProviderAplanAnalysis *analysisView, const char *pixmapname, QWidget *parent)
    : TaskBox(Gui::BitmapFactory().pixmap(pixmapname), tr("APLAN analysis parameters"), true, parent),
      workingDir{},
      proxy(nullptr),
      analysisView(analysisView)
{
    this->proxy = new QWidget(this);
    this->ui = new Ui_TaskAplanAnalysis();
    this->ui->setupUi(this->proxy);

    // Buttons
    QObject::connect(this->ui->tb_choose_working_dir, SIGNAL(clicked()), this, SLOT(chooseWorkingDir()));

    this->groupLayout()->addWidget(proxy);
}

TaskAplanAnalysis::~TaskAplanAnalysis()
{
    delete this->ui;
}

void TaskAplanAnalysis::chooseWorkingDir()
{
    Aplan::AplanAnalysis *analysis = static_cast<Aplan::AplanAnalysis *>(this->analysisView->getObject());
    std::string workingDir{analysis->WorkingDir.getStrValue()};
    QString dir = workingDir.empty() ? QDir::homePath() : QString::fromStdString(workingDir);
    QFileDialog::Options options = QFileDialog::ShowDirsOnly | QFileDialog::DontResolveSymlinks;
    QString qPath = QFileDialog::getExistingDirectory(0, tr("Choose APLAN working directory"), dir, options);
    if (!qPath.isEmpty())
    {
        this->ui->le_working_dir->setText(qPath);
        this->workingDir = qPath.toStdString();
    }
}

const std::string TaskAplanAnalysis::getWorkingDirectory() const
{
    return this->workingDir;
}

void TaskAplanAnalysis::setWorkingDirectory(const std::string &path)
{
    this->workingDir = path;
    this->ui->le_working_dir->setText(QString::fromStdString(this->workingDir));
}

const std::string TaskAplanAnalysis::getAnalysisLabel() const
{
    return this->ui->le_analysis_label->text().toStdString();
}

void TaskAplanAnalysis::setAnalysisLabel(const std::string &label)
{
    this->ui->le_analysis_label->setText(QString::fromStdString(label));
}

//**************************************************************************
// TaskDialog
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TaskDlgAplanAnalysis::TaskDlgAplanAnalysis(ViewProviderAplanAnalysis *analysisView)
    : analysisView{analysisView}
{
    this->analysis = static_cast<Aplan::AplanAnalysis *>(this->analysisView->getObject());
    this->parameter = new TaskAplanAnalysis(analysisView, "APLAN_Analysis");

    std::string workingDir{this->analysis->WorkingDir.getStrValue()};
    this->parameter->setWorkingDirectory(workingDir);

    std::string analysisLabel{this->analysis->Label.getStrValue()};
    this->parameter->setAnalysisLabel(analysisLabel);

    Gui::TaskView::TaskDialog::Content.push_back(this->parameter);
}

//==== calls from the TaskView ===============================================================

void TaskDlgAplanAnalysis::open()
{
    // a transaction is already open at creation time of the panel
    if (!Gui::Command::hasPendingCommand())
    {
        QString msg = QObject::tr("Analysis");
        Gui::Command::openCommand((const char *)msg.toUtf8());
        this->analysisView->setVisible(true);
    }
}

bool TaskDlgAplanAnalysis::accept()
{
    std::string workingDir{this->parameter->getWorkingDirectory()};
    if (!workingDir.empty())
        this->analysis->WorkingDir.setValue(workingDir);
    else
    {
        QMessageBox::warning(Gui::getMainWindow(), tr("Missing working directory"),
                             QString::fromLatin1("Please select a working directory before continuing."));
        return false;
    }

    std::string analysisLabel{this->parameter->getAnalysisLabel()};
    if (!analysisLabel.empty())
        this->analysis->Label.setValue(analysisLabel);

    Gui::Command::doCommand(Gui::Command::Doc, "App.ActiveDocument.recompute()");
    if (!this->analysisView->getObject()->isValid())
        throw Base::RuntimeError(this->analysisView->getObject()->getStatusString());
    Gui::Command::doCommand(Gui::Command::Gui, "Gui.activeDocument().resetEdit()");
    Gui::Command::commitCommand();

    return true;
}

bool TaskDlgAplanAnalysis::reject()
{
    // Roll back the changes
    Gui::Command::abortCommand();
    Gui::Command::doCommand(Gui::Command::Gui,"Gui.activeDocument().resetEdit()");
    Gui::Command::updateActive();

    return true;
}

#include "moc_TaskAplanAnalysis.cpp"
