# ************************************************************************************************
# ****** sub directories**************************************************************************
# ************************************************************************************************

add_subdirectory(App)

if(BUILD_GUI)
    add_subdirectory(Gui)
endif(BUILD_GUI)


# ************************************************************************************************
# ****** Python non Gui packages and modules *****************************************************
# ************************************************************************************************

SET(AplanBaseModules_SRCS
    Init.py
    InitGui.py
    ObjectsAplan.py
)

SET(AplanCommands_SRCS
    aplancommands/__init__.py
    aplancommands/commands.py
    aplancommands/manager.py
)

SET(AplanObjects_SRCS
    aplanobjects/__init__.py
    aplanobjects/base_aplanpythonobject.py
    aplanobjects/compound.py
    aplanobjects/graphs.py
    aplanobjects/part_filter.py
    aplanobjects/topo_constraints.py
)

SET(AplanSolvers_SRCS
    # AND-OR graph generators
    aplansolvers/aplan_aog_generators/__init__.py
    # Connection detectors
    aplansolvers/aplan_connection_detectors/__init__.py
    aplansolvers/aplan_connection_detectors/base_connection_detector.py
    aplansolvers/aplan_connection_detectors/swell_occt.py
    # Obstruction detectors
    aplansolvers/aplan_obstruction_detectors/__init__.py
)

SET(AplanTools_SRCS
    aplantools/__init__.py
    aplantools/aplanutils.py
)

SET(AplanAllScripts
    ${AplanBaseModules_SRCS}
    ${AplanCommands_SRCS}
    ${AplanObjects_SRCS}
    ${AplanSolvers_SRCS}
    ${AplanTools_SRCS}
)

ADD_CUSTOM_TARGET(AplanScriptsTarget ALL
    SOURCES ${AplanAllScripts}
)
fc_copy_sources(AplanScriptsTarget "${CMAKE_BINARY_DIR}/Mod/Aplan" ${AplanAllScripts})


# install directories for Python packages (for make install)
INSTALL(FILES ${AplanBaseModules_SRCS} DESTINATION Mod/Aplan)
INSTALL(FILES ${AplanCommands_SRCS} DESTINATION Mod/Aplan/aplancommands)
INSTALL(FILES ${AplanObjects_SRCS} DESTINATION Mod/Aplan/aplanobjects)
INSTALL(FILES ${AplanSolvers_SRCS} DESTINATION Mod/Aplan/aplansolvers)
INSTALL(FILES ${AplanTools_SRCS} DESTINATION Mod/Aplan/aplantools)


# ************************************************************************************************
# ****** Python Gui packages and modules *********************************************************
# ************************************************************************************************

SET(AplanGuiTaskPanels_SRCS
    aplantaskpanels/__init__.py
    aplantaskpanels/task_part_filter.py
    aplantaskpanels/task_topo_constraints.py
)

SET(AplanGuiViewProvider_SRCS
    aplanviewprovider/__init__.py
    aplanviewprovider/view_compound.py
    aplanviewprovider/view_part_filter.py
    aplanviewprovider/view_topo_constraints.py
)

SET(AplanGuiWebApp_SRCS
    # CSS
    aplanwebapp/static/css/error.css
    aplanwebapp/static/css/style.css
    # JS
    aplanwebapp/static/js/connection_graph.js
    aplanwebapp/static/js/error.js
    # JSON
    aplanwebapp/static/json/config_params.json
    # HTML
    aplanwebapp/templates/connection_graph.html
    aplanwebapp/templates/error_404.html
    aplanwebapp/templates/error_500.html
    # Python
    aplanwebapp/__init__.py
    aplanwebapp/api.py
    aplanwebapp/browser.py
    aplanwebapp/server.py
)

SET(AplanAllGuiScripts
    ${AplanGuiTaskPanels_SRCS}
    ${AplanGuiViewProvider_SRCS}
    ${AplanGuiWebApp_SRCS}
)

if(BUILD_GUI)
    ADD_CUSTOM_TARGET(AplanGuiScriptsTarget ALL
        SOURCES ${AplanAllGuiScripts}
    )
    fc_copy_sources(AplanGuiScriptsTarget "${CMAKE_BINARY_DIR}/Mod/Aplan" ${AplanAllGuiScripts})

    # install directories for Python packages (for make install)
    INSTALL(FILES ${AplanGuiTaskPanels_SRCS} DESTINATION Mod/Aplan/aplantaskpanels/)
    INSTALL(FILES ${AplanGuiViewProvider_SRCS} DESTINATION Mod/Aplan/aplanviewprovider/)
    INSTALL(FILES ${AplanGuiWebApp_SRCS} DESTINATION Mod/Aplan/aplanwebapp/)
endif(BUILD_GUI)