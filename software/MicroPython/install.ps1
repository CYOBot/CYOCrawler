Write-Host "Start setting up production code for CYOCrawler v2.0" -ForegroundColor Green

$port = Get-WMIObject Win32_SerialPort | where{$_.Description -like "Silicon*"} | Select-Object DeviceID, Description
Write-Host "Found $($port.DeviceID)"

Write-Host "Invoke cyobot conda environment" -ForegroundColor Green
Invoke-Expression "conda activate cyobot"

Write-Host "Erase flash of current board" -ForegroundColor Green
Invoke-Expression "esptool -p $($port.DeviceID) erase_flash"

$currentDir = Get-Location
$imageFileName = "cyobot-os.bin"
$imageFilePath = Join-Path -Path $currentDir -ChildPath $imageFileName
if (Test-Path -Path $imageFilePath -PathType Leaf) {
    Write-Host "The file '$imageFileName' exists in the current directory." -ForegroundColor Green
} else {
    Write-Host "The file '$imageFileName' does not exist in the current directory." -ForegroundColor Red
    Exit 1
}

Write-Host "Upload CYOBot OS to the board" -ForegroundColor Green
Invoke-Expression "esptool --chip esp32 --port $($port.DeviceID) --baud 460800 write_flash -z 0x1000 cyobot-os.bin"

$currentDir = Get-Location
$rootFolder = Join-Path -Path $currentDir -ChildPath "pyboard"
Set-Location $rootFolder

Write-Host "Copy startup files to board" -ForegroundColor Green
Invoke-Expression "rshell -p $($port.DeviceID) -b 115200 rsync . /pyboard"