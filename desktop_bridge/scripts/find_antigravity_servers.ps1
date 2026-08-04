param()

$processes = Get-CimInstance Win32_Process |
    Where-Object { $_.Name -like 'language_server*' }

$listeningByPid = @{}
netstat -ano -p tcp |
    Select-String 'LISTENING' |
    ForEach-Object {
        $parts = ($_ -replace '\s+', ' ').Trim().Split(' ')
        if ($parts.Length -ge 5) {
            $localAddress = $parts[1]
            $pid = $parts[4]
            if (-not $listeningByPid.ContainsKey($pid)) {
                $listeningByPid[$pid] = @()
            }
            $listeningByPid[$pid] += $localAddress
        }
    }

$results = foreach ($process in $processes) {
    $commandLine = $process.CommandLine
    if (-not $commandLine) {
        continue
    }

    $csrfToken = $null
    $extensionServerPort = $null
    $workspaceId = $null
    $subclientType = $null
    $cloudCodeEndpoint = $null

    if ($commandLine -match '--csrf_token\s+([^\s]+)') {
        $csrfToken = $matches[1]
    }
    if ($commandLine -match '--extension_server_port\s+([^\s]+)') {
        $extensionServerPort = $matches[1]
    }
    if ($commandLine -match '--workspace_id\s+([^\s]+)') {
        $workspaceId = $matches[1]
    }
    if ($commandLine -match '--subclient_type\s+([^\s]+)') {
        $subclientType = $matches[1]
    }
    if ($commandLine -match '--cloud_code_endpoint\s+([^\s]+)') {
        $cloudCodeEndpoint = $matches[1]
    }

    $pidKey = [string]$process.ProcessId
    $listeningPorts = @($listeningByPid[$pidKey])
    $recommendedAddress = if ($listeningPorts.Count -gt 0) {
        $listeningPorts[-1]
    } else {
        $null
    }

    [PSCustomObject]@{
        processId = $process.ProcessId
        name = $process.Name
        recommendedLsAddress = $recommendedAddress
        listeningAddresses = $listeningPorts
        csrfToken = $csrfToken
        extensionServerPort = $extensionServerPort
        workspaceId = $workspaceId
        subclientType = $subclientType
        cloudCodeEndpoint = $cloudCodeEndpoint
        commandLine = $commandLine
    }
}

$results | ConvertTo-Json -Depth 4
