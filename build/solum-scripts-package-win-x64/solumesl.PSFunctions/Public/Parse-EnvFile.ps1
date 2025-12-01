function Parse-EnvFile {
    param(
        [string]$FilePath,
        [switch]$SetAsEnvironmentVariables
    )

    # Check if the file exists
    if (-Not (Test-Path $FilePath)) {
        Write-Host "File not found: $FilePath"
        return
    }

    # Read the file and process each line
    Get-Content $FilePath | ForEach-Object {
        # Trim whitespace for each line
        $line = $_.Trim()

        # Skip empty lines and comments
        if ($line -eq "" -or $line.StartsWith("#")) {
            return
        }

        # Split line into key and value
        $keyValue = $line -split '=', 2

        # Check if the line was valid with one '='
        if ($keyValue.Count -ne 2) {
            Write-Warning "Ignoring invalid line: $line"
            return
        }

        # Assign variable dynamically within the script
        Set-Variable -Name $keyValue[0].Trim() -Value $keyValue[1].Trim() -Scope Script

        # Optionally, set as environment variable
        if ($SetAsEnvironmentVariables) {
            [System.Environment]::SetEnvironmentVariable($keyValue[0].Trim(), $keyValue[1].Trim(), [System.EnvironmentVariableTarget]::Process)
        }
    }
}

# Example usage
# Parse the .env file and set variables in the script scope
#Parse-EnvFile -FilePath ".\.env"

# Parse the .env file and set variables as environment variables
# Parse-EnvFile -FilePath ".\.env" -SetAsEnvironmentVariables