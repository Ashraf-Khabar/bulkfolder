#define MyAppName "BulkFolder"
; Récupère la version de l'EXE généré par PyInstaller
#define MyAppVersion GetFileVersion("dist\BulkFolder\BulkFolder.exe")
#define MyAppPublisher "BulkFolder Contributors"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; L'emplacement de sortie doit correspondre à votre GitHub Action
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
; Inclut l'exécutable principal
Source: "dist\BulkFolder\BulkFolder.exe"; DestDir: "{app}"; Flags: ignoreversion
; Inclut tout le dossier _internal (Python + dépendances)
Source: "dist\BulkFolder\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\BulkFolder.exe"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\BulkFolder.exe"; Tasks: desktopicon