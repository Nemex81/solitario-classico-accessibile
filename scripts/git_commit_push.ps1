param(
    [string]$FilePath = "docs/3 - coding plans/PLAN_game-engine-refactoring_v3.6.0.md",
    [string]$Branch = "supporto-audio-centralizzato"
)

Write-Host "== Verifica repository =="
git status --porcelain

Write-Host "\n== Diff per il file: $FilePath =="
git --no-pager diff -- $FilePath || Write-Host "Nessun diff o file non tracciato"

$confirm = Read-Host "Vuoi procedere con stage, commit e push di '$FilePath' verso branch '$Branch'? (y/N)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "Operazione annullata dall'utente."; exit 1
}

$msg = Read-Host "Inserisci il commit message"
if ([string]::IsNullOrWhiteSpace($msg)) {
    Write-Host "Commit message vuoto: annullo."; exit 1
}

Write-Host "Staging: $FilePath"
git add -- "$FilePath"
if ($LASTEXITCODE -ne 0) { Write-Host "git add fallito"; exit $LASTEXITCODE }

Write-Host "Commit: $msg"
git commit -m "$msg"
if ($LASTEXITCODE -ne 0) { Write-Host "git commit fallito o nulla da committare"; exit $LASTEXITCODE }

Write-Host "Push su origin/$Branch"
git push origin "$Branch"
if ($LASTEXITCODE -ne 0) { Write-Host "git push fallito"; exit $LASTEXITCODE }

Write-Host "Operazione completata con successo."