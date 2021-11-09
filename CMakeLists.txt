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

SET(AplanAllScripts
    ${AplanBaseModules_SRCS}
    ${AplanCommands_SRCS}
)

ADD_CUSTOM_TARGET(AplanScriptsTarget ALL
    SOURCES ${AplanAllScripts}
)
fc_copy_sources(AplanScriptsTarget "${CMAKE_BINARY_DIR}/Mod/Aplan" ${AplanAllScripts})


# install directories for Python packages (for make install)
INSTALL(FILES ${AplanBaseModules_SRCS} DESTINATION Mod/Aplan)
INSTALL(FILES ${AplanCommands_SRCS} DESTINATION Mod/Aplan/aplancommands)


# ************************************************************************************************
# ****** Python Gui packages and modules *********************************************************
# ************************************************************************************************


