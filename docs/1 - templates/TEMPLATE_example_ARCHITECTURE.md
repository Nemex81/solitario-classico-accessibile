# ??? ARCHITECTURE.md - [Project Name]
> Documentazione architetturale principale. Per linee guida di stile e
> policy leggere `.github/copilot-instructions.md`.
---
## ?? Purpose
Descrive l'architettura ad alto livello: i layer, le dipendenze e le scelte
principali. Evita dettagli implementativi.
---
## ?? System Overview
Breve paragrafo su scopo del progetto e paradigmi architetturali.
---
## ??? Layer Architecture
```
PRESENTATION ? APPLICATION ? DOMAIN ? INFRASTRUCTURE
```
- **Domain**: logica business, zero dipendenze esterne
- **Application**: orchestrazione, dipende da Domain
- **Presentation**: UI e formattatori, dipende da Application
- **Infrastructure**: storage, servizi esterni, implementa interfacce Domain
*Aggiungi qui diagrammi o note specifiche del progetto.*
---
## ?? Tech Stack (esempio)
- Python 3.x – linguaggio principale
- wxPython – GUI
- pytest – testing
*(Adatta alla tua stack)*
---
*(Continua con dettagli rilevanti come direttive di dipendenza o pattern
speciali, ma mantieni il documento snello.)*
