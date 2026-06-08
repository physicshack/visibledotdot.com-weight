# import-to-firebase.ps1
# Imports weight-tracker-backup JSON to Firebase Realtime Database
# Usage: .\scripts\import-to-firebase.ps1
#
# PREREQUISITES:
#   1. Firebase security rules must allow write to /health/{username}
#      Add to rules:  "health": { "$userId": { ".read": true, ".write": true } }
#   2. Run from repo root

param(
    [string]$BackupFile = "weight-tracker-backup-2026-06-08.json",
    [string]$FirebaseUrl = "https://paymind-b1d51-default-rtdb.europe-west1.firebasedatabase.app",
    [string]$Username = "davejfowler"
)

$ErrorActionPreference = "Stop"

Write-Host "=== visible.. weight Firebase importer ===" -ForegroundColor Cyan
Write-Host "Target: /health/$Username" -ForegroundColor Cyan
Write-Host ""

# Load backup
if (-not (Test-Path $BackupFile)) {
    Write-Error "Backup file not found: $BackupFile"
    exit 1
}

$backup = Get-Content $BackupFile -Raw -Encoding UTF8 | ConvertFrom-Json
Write-Host "Backup loaded: $($backup.weightData.Count) weight entries, $($backup.journalData.Count) journal entries"

# Convert weightData array to keyed object (Firebase requires objects, not arrays)
$weightObj = @{}
foreach ($entry in $backup.weightData) {
    # Key: date or date_HHMM for timestamped entries
    $key = $entry.date
    if ($entry.time) {
        $safeTime = $entry.time -replace ":", ""
        $key = "$($entry.date)_$safeTime"
    }
    $weightObj[$key] = $entry
}
Write-Host "Weight entries keyed: $($weightObj.Count)"

# Convert journalData array to keyed object
$journalObj = @{}
foreach ($entry in $backup.journalData) {
    $journalObj[$entry.date] = $entry
}
Write-Host "Journal entries keyed: $($journalObj.Count)"

# Build payload
$payload = @{
    weightData  = $weightObj
    journalData = $journalObj
} | ConvertTo-Json -Depth 10

# Upload to Firebase REST API
# No auth needed if rules allow public write to /health/{userId}
$uri = "$FirebaseUrl/health/$Username.json"
Write-Host ""
Write-Host "Uploading to: $uri" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri $uri -Method Put -Body $payload -ContentType "application/json; charset=utf-8"
    Write-Host ""
    Write-Host "SUCCESS: Data written to /health/$Username" -ForegroundColor Green
    Write-Host "Weight entries uploaded: $($weightObj.Count)"
    Write-Host "Journal entries uploaded: $($journalObj.Count)"
    Write-Host ""
    Write-Host "Open the app, click the 👤 Guest button, and enter: $Username"
} catch {
    $statusCode = $_.Exception.Response?.StatusCode?.value__
    Write-Host ""
    Write-Error "Upload failed (HTTP $statusCode): $_"
    Write-Host ""
    Write-Host "If you got a 401 Permission Denied, update Firebase security rules:" -ForegroundColor Yellow
    Write-Host '  "health": { "$userId": { ".read": true, ".write": true } }'
    Write-Host "Then re-run this script."
    exit 1
}
