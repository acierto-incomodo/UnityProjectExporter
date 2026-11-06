!macro preInit
  SetRegView 64
  WriteRegExpandStr HKLM "${INSTALL_REGISTRY_KEY}" InstallLocation "$APPDATA\StormGamesStudios\Programs\Unity Project Exporter"
  WriteRegExpandStr HKCU "${INSTALL_REGISTRY_KEY}" InstallLocation "$APPDATA\StormGamesStudios\Programs\Unity Project Exporter"
!macroend

!macro customInit
  StrCpy $INSTDIR "$APPDATA\StormGamesStudios\Programs\Unity Project Exporter"
!macroend