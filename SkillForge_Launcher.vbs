Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\Joseph I Thomas\universal-skill-creator"
appCmd = Chr(34) & "C:\Python314\pythonw.exe" & Chr(34) & " " & Chr(34) & "C:\Users\Joseph I Thomas\universal-skill-creator\desktop_app.py" & Chr(34)
WshShell.Run appCmd, 1, False
