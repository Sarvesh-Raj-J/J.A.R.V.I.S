Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strPath = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strPath
WshShell.Run """" & strPath & "\..\venv\Scripts\pythonw.exe"" """ & strPath & "\jarvis_launcher.pyw""", 0, False
Set WshShell = Nothing
Set fso = Nothing
