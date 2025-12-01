
Import-Module -Name "$PSScriptRoot\solumesl.PSFunctions" -Force -Scope Local

# Disable SSL Valdiation
add-type @"
using System.Net;
using System.Security.Cryptography.X509Certificates;
public class TrustAllCertsPolicy : ICertificatePolicy {
    public bool CheckValidationResult(
        ServicePoint srvPoint, X509Certificate certificate,
        WebRequest request, int certificateProblem) {
        return true;
    }
}
"@
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy

# Set the TLS version to 1.2 or 1.3
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13

Function Download-Files {
    param(
        [Parameter(Mandatory = $true)]
        [array]$Urls,
        [Parameter(Mandatory = $true)]
        [string]$DestinationPath
    )

    foreach ($url in $Urls) {
        $fileName = $url.fileName
        $url = $url.url
        $destinationFile = Join-Path -Path $DestinationPath -ChildPath $fileName
        # Check if the file already exists
        if (Test-Path $destinationFile) {
            Write-Host "File $destinationFile already exists"
            return
        }
        Write-Host "Downloading $url to $destinationFile"
        Invoke-WebRequest -Uri $url -OutFile $destinationFile
    }
}

Set-Location "$PSScriptRoot\..\.."

Parse-EnvFile -FilePath "$PSScriptRoot\..\..\.env" -SetAsEnvironmentVariables

Remove-PycacheFolders -Path "$PSScriptRoot\..\.."

# List of files and folders to compress
$filesAndFolders = @(
    "bin\",
    "data\",
    "modules\",
    "services\",
    "db\",
    "scripts\",
    "*.bat",
    "*.py",
    ".env"
)


Set-Location "$PSScriptRoot\..\.."

# write current directory to host
Write-Host "Current directory: $(Get-Location)"

$python_version = [System.Environment]::GetEnvironmentVariable("PYTHON_VERSION", [System.EnvironmentVariableTarget]::Process)
$version = [System.Environment]::GetEnvironmentVariable("VERSION", [System.EnvironmentVariableTarget]::Process)

# Target zip file name
$zipFileName = "aims-saas-adapater-kimsladen-win-x64-$python_version-v$version.zip"

# Compress the files and folders into the zip file
Compress-7zArchive -SevenZipPath "$PSScriptRoot\bin\7z\x64\7za.exe" -Path $filesAndFolders -DestinationPath $zipFileName

# Force move the zip file to dist folder
Move-Item -Path $zipFileName -Destination "$PSScriptRoot\..\..\dist\$zipFileName" -Force

