function Compress-7zArchive {
    param (
        [Parameter(Mandatory = $true)][string]$SevenZipPath,
        [Parameter(Mandatory = $true)][string[]]$Path,
        [Parameter(Mandatory = $true)][string]$DestinationPath
    )

    if (-not (Test-Path -Path $SevenZipPath)) {
        Write-Warning "7zFilePath not found: $SevenZipPath"
        return
    }

    # Create an array of paths with each path wrapped in double quotes
    $PathList = $Path | ForEach-Object { "`"$_`"" }

    # Construct arguments for 7za.exe
    $arguments = @(
        'a'
        '-bsp1'
        '-tzip'
        "`"$DestinationPath`""
    ) + $PathList

    try {
        Write-Output "Compressing files and folders..."
        & $SevenZipPath $arguments
        Write-Output "Compression complete: $DestinationPath"
    } catch {
        Write-Error "An error occurred during compression: $_"
    }
}

# Example usage
# Set the working directory
#Set-Location -Path "C:\Users\GlennGoffin\Git\solum-esl\utils\aims-superset-win-x64"
#$zipFileName = "aims-superset-win-x64.zip"
#
#$filesAndFolders = @(
#    "bin\",
#    "scripts\",
#    "superset\",
#    "run-superset-debug.bat",
#    ".env"
#)
#
## Call the function with correct parameters
#Compress-7zArchive -SevenZipPath "C:\Users\GlennGoffin\Git\solum-esl\utils\aims-superset-win-x64\scripts\bin\7z\x64\7za.exe" -Path $filesAndFolders -DestinationPath $zipFileName
