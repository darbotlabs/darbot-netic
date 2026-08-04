# Ensure script is running as Administrator
$IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $IsAdmin) {
    Write-Host "Not running as Administrator. Relaunching with elevated privileges..."
    $script = $MyInvocation.MyCommand.Definition
    Start-Process PowerShell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$script`"" -Verb RunAs
    exit
}

# Path to add
$ffmpegBin = "d:\0GH_PROD\darbot-netic\ffmpeg\ffmpeg-7.1.1-essentials_build\bin"

# Get current system PATH
$oldPath = [Environment]::GetEnvironmentVariable('Path', [EnvironmentVariableTarget]::Machine)
if ($oldPath -notlike "*${ffmpegBin}*") {
    $newPath = $oldPath + ";" + $ffmpegBin
    [Environment]::SetEnvironmentVariable('Path', $newPath, [EnvironmentVariableTarget]::Machine)
    Write-Host "FFmpeg path added to system PATH. You may need to restart your terminal or log out/in for changes to take effect."
} else {
    Write-Host "FFmpeg path is already present in system PATH."
}
