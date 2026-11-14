Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
folder = FSO.GetParentFolderName(WScript.ScriptFullName)
launcher = folder & "\LAUNCH_SAINTS_GYM.ps1"
If Not FSO.FileExists(launcher) Then
    MsgBox "LAUNCH_SAINTS_GYM.ps1 is missing from:" & vbCrLf & folder, vbCritical, "Saints Gym"
    WScript.Quit 1
End If
If Not FSO.FileExists(folder & "\SAINTS_GYM_STARTING.html") Then
    MsgBox "SAINTS_GYM_STARTING.html is missing from:" & vbCrLf & folder, vbCritical, "Saints Gym"
    WScript.Quit 1
End If
command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & launcher & """"
WshShell.Run command, 0, False
