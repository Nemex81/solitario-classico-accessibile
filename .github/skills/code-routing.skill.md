---
name: code-routing
description: >
  Regole di classificazione delle fasi di implementazione per Agent-CodeRouter.
  Determina deterministicamente se una fase va ad Agent-Code o Agent-CodeUI.
---

# Skill: Code Routing

## Regola Primaria

Analizza il testo della fase in docs/TODO.md e del PLAN corrispondente.
Applica pattern matching nell'ordine indicato. Prima regola che corrisponde vince.

## Pattern GUI → Agent-CodeUI

Corrisponde se il testo della fase contiene almeno uno di:

- Classi wxPython: `wx.`, `Panel`, `Dialog`, `Frame`, `Button`, `ListCtrl`,
  `TextCtrl`, `StaticText`, `Notebook`, `Menu`, `Toolbar`, `Sizer`
- Keyword UI: `interfaccia`, `schermata`, `finestra`, `layout`, `widget`,
  `componente UI`, `form`, `visualizzazione`, `rendering`, `GUI`
- Accessibilità UI: `SetLabel`, `SetFocus`, `TAB order`, `acceleratore tastiera`

## Pattern Non-GUI → Agent-Code

Corrisponde se il testo della fase contiene almeno uno di:

- Layer applicativo: `domain`, `application`, `service`, `use case`,
  `repository`, `entity`, `value object`, `model`
- Infrastruttura: `sqlite`, `db`, `database`, `file system`, `config`,
  `persistence`, `serializzazione`, `JSON`, `pickle`
- Logic/Control: `algoritmo`, `logica`, `regola`, `validazione`, `calcolo`,
  `business logic`, `controller`, `handler`, `event`
- Audio/sistema: `audio`, `pygame`, `sound`, `mixer`, `thread`, `processo`
- Test/build: `test`, `pytest`, `coverage`, `build`, `cx_freeze`, `script`

## Caso Ambiguo

Se una fase contiene pattern di entrambe le categorie, segnala all'utente
e attendi risposta con questo formato esatto:

```
ROUTING AMBIGUO — Fase: <nome fase>
Pattern GUI rilevati: <lista>
Pattern non-GUI rilevati: <lista>
Opzione A: Agent-CodeUI (implementa tutto nella fase)
Opzione B: Agent-Code (implementa tutto nella fase)
Opzione C: Dividi la fase in due sotto-task
Quale opzione scegli?
```

## Espandibilità

Per aggiungere nuovi agenti specializzati: aggiungi una sezione
"Pattern <dominio> → Agent-<Nome>" prima della sezione "Caso Ambiguo".
Il primo pattern che corrisponde nell'ordine vince.
