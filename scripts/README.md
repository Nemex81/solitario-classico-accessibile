Questo script PowerShell facilita lo staging, il commit e il push di un singolo file (per sicurezza).

Uso (PowerShell):

1. Apri PowerShell nella root del progetto:
   ```powershell
   cd "C:\Users\nemex\OneDrive\Documenti\GitHub\solitario-classico-accessibile"
   ```
2. Esegui lo script (potrebbe richiedere di impostare l'esecuzione di script):
   ```powershell
   # Se necessario:
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

   .\scripts\git_commit_push.ps1
   ```

3. Segui le richieste: conferma, inserisci il messaggio di commit.

Note di sicurezza:
- Lo script non memorizza token o credenziali.
- Assicurati di avere `git` configurato e le credenziali remote pronte (PAT, SSH agent, o credenziali Windows).
- Lo script esegue `git add` solo sul file predefinito `docs/3 - coding plans/PLAN_game-engine-refactoring_v3.6.0.md`. Per altri file modifica il parametro `-FilePath`.

Esempio avanzato (committare un file diverso):
```powershell
.\scripts\git_commit_push.ps1 -FilePath "path\to\altro_file.md" -Branch "nome-branch"
```

Se preferisci, posso generare anche una versione che esegue `git add -A` e chiede conferma prima di continuare.