---
name: validate-accessibility
description: >
  Checklist accessibilità WAI-ARIA per componenti wxPython.
  Richiamabile da Agent-Validate e Agent-Code per verificare
  che ogni componente UI sia navigabile da tastiera e compatibile
  con screen reader NVDA su Windows 11.
---

# Skill: Validate Accessibility

## Checklist obbligatoria per ogni componente UI

Per ogni dialog, panel o controllo wxPython verifica:

- [ ] `SetLabel()` con testo descrittivo e non ambiguo
- [ ] Bottoni critici con acceleratori tastiera (`&OK`, `&Annulla`)
- [ ] `SetTitle()` semantico sul dialog/frame
- [ ] `SetFocus()` impostato sul primo controllo logico all'apertura
- [ ] `ESC` chiude il dialog senza effetti collaterali
- [ ] `TAB` naviga i controlli in ordine logico (usa `MoveAfterInTabOrder` se necessario)
- [ ] Nessun feedback visivo esclusivo (colore, icona) senza alternativa testuale

## Requisiti NVDA specifici

- Evitare aggiornamenti dinamici silenziosi: usare `wx.PostEvent` o
  `AccessibleDescription` per notificare cambiamenti di stato
- Label su tutti i controlli anche se visivamente ovvi
- No testo in immagini o icone senza `alt` testuale equivalente

## Output atteso

Report strutturato:
```
Componente: <NomeClasse>
Checklist: [N/7] voci OK
Issues: <lista problemi rilevati o "nessuno">
Stato: PASS / FAIL
```
