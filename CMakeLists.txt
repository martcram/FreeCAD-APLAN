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
    aplanobjects/topo_constraints.py
)

SET(AplanTools_SRCS
    aplantools/__init__.py
    aplantools/aplanutils.py
)

SET(AplanAllScripts
    ${AplanBaseModules_SRCS}
    ${AplanCommands_SRCS}
    ${AplanObjects_SRCS}
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
INSTALL(FILES ${AplanTools_SRCS} DESTINATION Mod/Aplan/aplantools)


# ************************************************************************************************
# ****** Python Gui packages and modules *********************************************************
# ************************************************************************************************

SET(AplanGuiViewProvider_SRCS
    aplanviewprovider/__init__.py
    aplanviewprovider/view_topo_constraints.py
)

SET(AplanAllGuiScripts
    ${AplanGuiViewProvider_SRCS}
)

if(BUILD_GUI)
    ADD_CUSTOM_TARGET(AplanGuiScriptsTarget ALL
        SOURCES ${AplanAllGuiScripts}
    )
    fc_copy_sources(AplanGuiScriptsTarget "${CMAKE_BINARY_DIR}/Mod/Aplan" ${AplanAllGuiScripts})

    # install directories for Python packages (for make install)
    INSTALL(FILES ${AplanGuiViewProvider_SRCS} DESTINATION Mod/Aplan/aplanviewprovider/)
endif(BUILD_GUI)