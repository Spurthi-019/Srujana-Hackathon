# Auto-commit script for Windows PowerShell
param(
    [int]$MinChanges = 3,
    [switch]$Force
)

function Get-GitStatus {
    $gitStatus = git status --porcelain
    $changes = @()
    
    if ($gitStatus) {
        foreach ($line in $gitStatus) {
            if ($line.Trim()) {
                $status = $line.Substring(0, 2)
                $file = $line.Substring(3)
                $changes += @{
                    Status = $status
                    File = $file
                }
            }
        }
    }
    
    return $changes
}

function Get-FileCategory {
    param([string]$filename)
    
    $ext = [System.IO.Path]::GetExtension($filename).ToLower()
    
    switch ($ext) {
        { $_ -in '.js', '.ts', '.jsx', '.tsx' } { return 'Frontend' }
        { $_ -in '.py', '.java', '.cs', '.cpp' } { return 'Backend' }
        { $_ -in '.css', '.scss', '.sass' } { return 'Styling' }
        { $_ -in '.json', '.xml', '.yml', '.yaml' } { return 'Config' }
        { $_ -in '.md', '.txt' } { return 'Docs' }
        { $_ -in '.sql' } { return 'Database' }
        default { return 'Misc' }
    }
}

function Generate-CommitMessage {
    param([array]$changes)
    
    $categories = @{}
    $addedFiles = @()
    $modifiedFiles = @()
    $deletedFiles = @()
    
    foreach ($change in $changes) {
        $category = Get-FileCategory $change.File
        if (-not $categories.ContainsKey($category)) {
            $categories[$category] = 0
        }
        $categories[$category]++
        
        switch ($change.Status.Trim()) {
            'A' { $addedFiles += $change.File }
            'M' { $modifiedFiles += $change.File }
            'D' { $deletedFiles += $change.File }
            'AM' { 
                $addedFiles += $change.File
                $modifiedFiles += $change.File
            }
        }
    }
    
    $topCategory = ($categories.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Name
    $commitType = if ($addedFiles.Count -gt $modifiedFiles.Count) { 'Add' } else { 'Update' }
    
    $message = "$commitType $topCategory files"
    
    $details = @()
    if ($addedFiles.Count -gt 0) { $details += "$($addedFiles.Count) added" }
    if ($modifiedFiles.Count -gt 0) { $details += "$($modifiedFiles.Count) modified" }
    if ($deletedFiles.Count -gt 0) { $details += "$($deletedFiles.Count) deleted" }
    
    if ($details.Count -gt 0) {
        $message += " (" + ($details -join ', ') + ")"
    }
    
    return $message
}

function Invoke-AutoCommit {
    param(
        [int]$MinChanges = 3,
        [switch]$Force
    )
    
    Write-Host "Checking for changes..." -ForegroundColor Blue
    
    $changes = Get-GitStatus
    $changeCount = $changes.Count
    
    Write-Host "Found $changeCount changed files" -ForegroundColor Yellow
    
    if (-not $Force -and $changeCount -lt $MinChanges) {
        Write-Host "Not enough changes yet ($changeCount/$MinChanges). Use -Force to commit anyway." -ForegroundColor Yellow
        return $false
    }
    
    try {
        Write-Host "Adding files to staging..." -ForegroundColor Cyan
        git add .
        
        $commitMessage = Generate-CommitMessage $changes
        Write-Host "Commit message: $commitMessage" -ForegroundColor Green
        
        Write-Host "Committing changes..." -ForegroundColor Cyan
        git commit -m $commitMessage
        
        Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
        git push
        
        Write-Host "Successfully committed and pushed $changeCount files!" -ForegroundColor Green
        return $true
        
    } catch {
        Write-Host "Error during git operations: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Execute the auto-commit
Write-Host "Auto-commit script starting..." -ForegroundColor Magenta
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Gray

$result = Invoke-AutoCommit -MinChanges $MinChanges -Force:$Force

if ($result) {
    Write-Host "All changes have been committed and pushed to GitHub!" -ForegroundColor Green
} else {
    Write-Host "Tip: Use 'auto-commit.ps1 -Force' to commit regardless of change count" -ForegroundColor Yellow
}