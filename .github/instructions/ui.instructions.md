---
applyTo: "src/presentation/**/*.py"
---

# UI Instructions — wxPython + Accessibilità NVDA

## Regole Obbligatorie per Ogni Componente

- Ogni `wx.Panel`, `wx.Dialog`, `wx.Frame`: `SetTitle()` semantico obbligatorio
- Ogni controllo interattivo: `SetLabel()` con testo non ambiguo
- Bottoni con azione critica: acceleratore tastiera (`&OK`, `&Annulla`)
- `SetFocus()` sul primo controllo logico all'apertura
- `ESC` su tutti i Dialog: chiude senza effetti collaterali
- Ordine TAB logico: usa `MoveAfterInTabOrder()` se ordine di creazione
  non corrisponde all'ordine di navigazione atteso

## Requisiti NVDA

- Nessun aggiornamento dinamico silenzioso: usa `wx.PostEvent` o
  `AccessibleDescription` per notificare cambiamenti di stato
- Nessun feedback esclusivamente visivo senza alternativa testuale
- Label su tutti i controlli, anche se visivamente ovvi

## Logging

- Ogni apertura/chiusura dialog: `logger.info("Dialog <Nome> aperto/chiuso")`
- Ogni azione utente su controllo critico: `logger.debug("Azione: <descrizione>")`

## Test GUI

- Componenti GUI marcati con `@pytest.mark.gui` — esclusi da CI normale
- Smoke test accessibilità con `wx.UIActionSimulator` dove disponibile
