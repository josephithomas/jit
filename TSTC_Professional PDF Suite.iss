; =============================================================================
; Titus II Teachers College - TSTC_Professional PDF Suite v5.0
; Inno Setup Script (Adobe Acrobat Studio Edition)
; Developed by Dr. Joseph I Thomas
;
; Place this .iss in the SAME folder as:
;   - dist\TSTC_Professional_PDF_Suite.exe   (PyInstaller output)
;   - app_icon.ico                          (required for SetupIconFile)
;   - logo.png / app_icon.png               (optional extras)
;
; Compile with Inno Setup 6.x (ISCC.exe or the IDE).
; =============================================================================

#define MyAppName      "TSTC Professional PDF Suite"
#define MyAppVersion   "5.0"
#define MyAppPublisher "Titus II Teachers College"
#define MyAppURL       "https://tituscollege.edu"
#define MyAppExeName   "TSTC_Professional_PDF_Suite.exe"
#define MyAppId        "{{A7B3C9D1-4E5F-6789-ABCD-EF0123456789}"

[Setup]
; Unique AppId – do not change after first public release
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
OutputDir=Output
OutputBaseFilename=TSTC_Professional_PDF_Suite_Setup
; ---------------------------------------------------------------------------
; ICON – must be a real .ico file next to this .iss (or use full path)
; Convert PNG → ICO first if you only have app_icon.png / logo.png
; ---------------------------------------------------------------------------
SetupIconFile=app_icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion=5.0.0.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main application executable produced by PyInstaller
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Optional: ship logo / icon assets next to the exe (useful for runtime icon loading)
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "app_icon.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; If you bundle extra data (e.g. sample PDFs, configs), add more Source lines here:
; Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

; =============================================================================
; NOTES FOR THE DEVELOPER
; =============================================================================
; 1. Create app_icon.ico BEFORE compiling:
;      - Use any PNG→ICO converter, or ImageMagick:
;          magick convert app_icon.png -define icon:auto-resize=256,128,64,48,32,16 app_icon.ico
;      - Place app_icon.ico in the SAME folder as this .iss file.
;
; 2. Folder layout expected at compile time:
;      TSTC_Professional PDF Suite.iss
;      app_icon.ico
;      logo.png          (optional)
;      app_icon.png      (optional)
;      dist\
;        TSTC_Professional_PDF_Suite.exe
;
; 3. Output will appear in:
;      Output\TSTC_Professional_PDF_Suite_Setup.exe
;
; 4. If you still get "path not found", open the .iss in Inno Setup IDE,
;    use Build → Compile, and read the exact line + path reported in the log.
; =============================================================================
