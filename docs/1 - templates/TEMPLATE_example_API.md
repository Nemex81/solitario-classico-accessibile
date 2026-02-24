# ?? API.md - [Project Name]
> **Public API reference**; version: v[X.Y.Z], updated YYYY-MM-DD.
> Questo template mostra il formato da seguire. Copia le sezioni `### ClassName`
> e `#### method()` per ogni API pubblica. Per linee guida dettagliate e esempi
> consultare `.github/copilot-instructions.md`.
---
## ?? Document Purpose
Riferimento rapido per le API pubbliche che altre parti del sistema consumano.
Non documenta metodi privati né dettagli implementativi.
---
## ??? Layered API Structure
Organizza le voci per layer (Domain, Application, Presentation) come mostrato
nell'esempio seguente.
### Example Class
```python
class ExampleService:
    """Brief description of the service's role"""
    def do_action(self, param: int) -> bool:
        """Esempio di metodo pubblico.
        Args:
            param: descrizione
        Returns:
            bool: descrizione
        """
```
Ripeti la struttura per ogni classe e metodo pubblico che diventa
contratto tra componenti.
---
*(Il resto del documento può essere completato con le voci specifiche del
progetto.)*
