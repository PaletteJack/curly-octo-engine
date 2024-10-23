[Setup]
AppName=Curly Octo Engine
AppVersion=1.0
DefaultDirName={autopf}\CurlyOctoEngine
DefaultGroupName=Curly Octo Engine
OutputDir=installer
OutputBaseFilename=CurlyOctoEngine_Setup
; Use absolute paths or make sure these paths are correct
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\CurlyOctoEngine.exe

; Add this to create the directory with proper permissions
[Dirs]
Name: "{app}"; Permissions: everyone-full

[Files]
; Specify the exact path to your exe
Source: "dist\CurlyOctoEngine.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Curly Octo Engine"; Filename: "{app}\CurlyOctoEngine.exe"
Name: "{commondesktop}\Curly Octo Engine"; Filename: "{app}\CurlyOctoEngine.exe"