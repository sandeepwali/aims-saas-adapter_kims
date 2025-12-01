function Remove-PycacheFolders {
    param (
        [string]$Path
    )

    if (-not (Test-Path -Path $Path)) {
        Write-Warning "Directory not found: $Path"
        return
    }

    $pycacheFolders = Get-ChildItem -Path $Path -Filter "__pycache__" -Recurse | 
                      Where-Object { $_.PSIsContainer }

    foreach ($folder in $pycacheFolders) {
        Remove-Item -Path $folder.FullName -Recurse -Force
    }
}