Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName)

' Build the command
pythonPath = scriptPath & "\.venv\Scripts\pythonw.exe"
mainScript = scriptPath & "\src\main.py"

' Check if a file argument was passed
If WScript.Arguments.Count > 0 Then
    filePath = WScript.Arguments(0)
    cmd = """" & pythonPath & """ """ & mainScript & """ """ & filePath & """"
Else
    cmd = """" & pythonPath & """ """ & mainScript & """"
End If

' Run without showing command window
WshShell.Run cmd, 0, False
