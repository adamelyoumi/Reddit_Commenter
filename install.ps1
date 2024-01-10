$venvName="comments"

Write-Host "Creating venv $venvName..."
& (Join-Path $env:USERPROFILE \AppData\Local\Programs\Python\Python311\python.exe) -m venv $venvName

Write-Host "Activating venv $venvName..."
& "$venvName\Scripts\Activate"

Write-Host "Installing dependencies from requirements.txt..."
& "$venvName\Scripts\pip" install -r requirements.txt



$downloadUrl = 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.70/win64/chromedriver-win64.zip'
$zipFilePath = Join-Path $env:TEMP 'chromedriver-win64.zip'
$extractPath = Join-Path $env:USERPROFILE '.cache\selenium\chromedriver\win32\118.0.5993.70'

Write-Host "Creating the destination directory if it doesn't exist"
New-Item -ItemType Directory -Force -Path $extractPath | Out-Null

Write-Host "Downloading the ChromeDriver zip file"
Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFilePath

Write-Host "Extracting the contents of the zip file"
Expand-Archive -Path $zipFilePath -DestinationPath $extractPath -Force

Write-Host "Removing the downloaded zip file"
Remove-Item -Path $zipFilePath -Force



$userName = $env:USERNAME

$sourcePath = ".\service_account.json"
$destinationPath = "C:\Users\$userName\AppData\Roaming\gspread"

try {
    New-Item -ItemType Directory -Force -Path $destinationPath | Out-Null
    Copy-Item -Path $sourcePath -Destination $destinationPath -Force
    Write-Host "File copied successfully to $destinationPath"
}
catch {
    Write-Host "Error: $_"
}

Read-Host -Prompt "Press Enter to exit"