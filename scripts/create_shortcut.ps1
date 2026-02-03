$desktop = [Environment]::GetFolderPath('Desktop')
$shortcutPath = "$desktop\Markdown Viewer.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = 'pythonw.exe'
$Shortcut.Arguments = 'C:\repo\markdown-viewer\src\main.py'
$Shortcut.WorkingDirectory = 'C:\repo\markdown-viewer'
$Shortcut.Description = 'Markdown Viewer'
$Shortcut.Save()

Write-Host "Shortcut created: $shortcutPath"
