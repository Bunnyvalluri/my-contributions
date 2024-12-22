<#
.SYNOPSIS
    Fills your GitHub contribution graph with backdated commits.
.PARAMETER Days
    Number of days to go back (default is 365).
.PARAMETER MaxCommits
    Maximum number of commits per day.
.PARAMETER Email
    Your GitHub email address.
.PARAMETER Push
    Automatically force pushes to origin main.
.EXAMPLE
    .\fill.ps1 -Days 365 -MaxCommits 15 -Email "your_email@gmail.com" -Push
#>

param (
    [int]$Days = 365,
    [int]$MaxCommits = 10,
    [string]$Email,
    [switch]$Push
)

# Check git is installed
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git is not installed or not in PATH."
    exit 1
}

# Resolve Email
if ([string]::IsNullOrEmpty($Email)) {
    $Email = git config user.email
}

if ([string]::IsNullOrEmpty($Email) -or $Email -like "*example.com*") {
    Write-Host "❌ Error: A valid GitHub email is required." -ForegroundColor Red
    Write-Host "Please run the script and specify your email:" -ForegroundColor Yellow
    Write-Host "  .\fill.ps1 -Email 'your_email@gmail.com'" -ForegroundColor Yellow
    exit 1
}

Write-Host "🟢 Git Email Configured: $Email" -ForegroundColor Green

# Init repository if needed
if (!(Test-Path .git)) {
    git init -b main
    Write-Host "Initialized local repository." -ForegroundColor Cyan
}

git config user.email $Email

$readmePath = "README.md"
if (!(Test-Path $readmePath)) {
    New-Item -Path $readmePath -ItemType File -Value "# My Contributions`n`nAutomated activity log.`n" | Out-Null
    git add $readmePath
    $startDateStr = (Get-Date).AddDays(-$Days).ToString("yyyy-MM-dd HH:mm:ss")
    git commit -m "Initial commit" --date "$startDateStr" | Out-Null
}

$startDate = (Get-Date).AddDays(-$Days)
$currentDate = Get-Date
$totalCommits = 0

Write-Host "🚀 Generating commits from $($startDate.ToString('yyyy-MM-dd')) to today..." -ForegroundColor Cyan

for ($i = 0; $i -le $Days; $i++) {
    $day = $startDate.AddDays($i)
    
    # Random commits count
    $dailyCommits = Get-Random -Minimum 5 -Maximum ($MaxCommits + 1)
    
    # Random minutes between 9 AM (540 mins) and 9 PM (1260 mins)
    $commitMinutes = @()
    for ($j = 0; $j -lt $dailyCommits; $j++) {
        $commitMinutes += Get-Random -Minimum 540 -Maximum 1260
    }
    $commitMinutes = $commitMinutes | Sort-Object
    
    foreach ($mins in $commitMinutes) {
        # Construct exact commit datetime
        $commitTime = Get-Date -Year $day.Year -Month $day.Month -Day $day.Day -Hour 0 -Minute 0 -Second 0
        $commitTime = $commitTime.AddMinutes($mins).AddSeconds((Get-Random -Minimum 0 -Maximum 60))
        
        # Skip future commits
        if ($commitTime -gt $currentDate) {
            continue
        }
        
        $formattedDate = $commitTime.ToString("yyyy-MM-dd HH:mm:ss")
        
        # Write to file
        Add-Content -Path $readmePath -Value "Contribution: $formattedDate"
        
        git add $readmePath
        
        # Force both author and committer dates
        $env:GIT_AUTHOR_DATE = $formattedDate
        $env:GIT_COMMITTER_DATE = $formattedDate
        
        git commit -m "Contribution: $formattedDate" --date "$formattedDate" | Out-Null
        $totalCommits++
    }
    
    if ($i % 30 -eq 0 -or $i -eq $Days) {
        Write-Host "  Processed $i/$Days days... ($totalCommits commits created)" -ForegroundColor Gray
    }
}

# Clear env variables
Remove-Item env:GIT_AUTHOR_DATE -ErrorAction SilentlyContinue
Remove-Item env:GIT_COMMITTER_DATE -ErrorAction SilentlyContinue

Write-Host "✅ Created $totalCommits commits successfully!" -ForegroundColor Green

if ($Push) {
    Write-Host "📤 Pushing to origin main..." -ForegroundColor Cyan
    git push -f origin main
    Write-Host "🚀 Pushed! Your contribution graph should update soon." -ForegroundColor Green
}
