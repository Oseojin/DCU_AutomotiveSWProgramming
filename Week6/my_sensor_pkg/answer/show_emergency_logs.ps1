# Pipe the existing ROS/WSL/SSH command's output into this script in PowerShell.
[CmdletBinding()]
param(
    [Parameter(ValueFromPipeline = $true)]
    [AllowNull()]
    [object]$InputObject
)

begin {
    # Unicode escapes keep this script compatible with PowerShell 5.1 encoding.
    $warningMessage = '[EMERGENCY_STOP] ' +
        [char]0xC804 + [char]0xBC29 + ' ' +
        [char]0xC7A5 + [char]0xC560 + [char]0xBB3C + ' ' +
        [char]0xAC10 + [char]0xC9C0 + '!'
}

process {
    if ($null -ne $InputObject) {
        # Remove ANSI controls before asking the PowerShell host to color text.
        $line = $InputObject.ToString() -replace '\x1b\[[0-?]*[ -/]*[@-~]', ''
        if ($line.Contains($warningMessage)) {
            Write-Host $warningMessage -ForegroundColor Red
        }
        else {
            Write-Host $line
        }
    }
}
