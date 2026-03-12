#define MyAppName "BulkFolder"
#define MyAppPublisher "BulkFolder Contributors"
; La version sera injectée par la ligne de commande GitHub
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif

[Setup]
AppId={{votre-guid-ici}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=Output
OutputBaseFilename=BulkFolder_Setup
SetupIconFile=src\assets\logo.ico
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\BulkFolder\BulkFolder.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\BulkFolder\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\BulkFolder.exe"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\BulkFolder.exe"; Tasks: desktopicon