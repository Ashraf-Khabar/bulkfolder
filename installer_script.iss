#define MyAppName "BulkFolder"
#define MyAppPublisher "BulkFolder Contributors"
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif

[Setup]
AppId={{BulkFolder-Unique-ID-12345}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=BulkFolder_Setup
SetupIconFile=src\assets\logo.ico
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Bulk folder organizer and renamer
VersionInfoVersion={#MyAppVersion}

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\BulkFolder\BulkFolder.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\BulkFolder\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\BulkFolder.exe"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\BulkFolder.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\BulkFolder.exe"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent