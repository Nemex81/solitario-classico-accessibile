---
type: design
feature: "[feature-slug]"
version: "vX.Y.Z"
status: DRAFT
agent: Agent-Design
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
---

# Design Document - [Feature Name]

> **FASE: CONCEPT & FLOW DESIGN**  
> Questo è uno scheletro. Per linee guida su quando e come scrivere e
> formattare un design document, consulta `.github/copilot-instructions.md`.
> Mantenere il documento conciso: descrivi logica e flussi, evita dettagli
> di implementazione.

---

## 📌 Metadata

- **Data Inizio**: YYYY-MM-DD
- **Stato**: [DRAFT | IN REVIEW | FROZEN]
- **Versione Target**: v[X.Y.Z] (ipotesi)
- **Autore**: AI Assistant + Nemex81

---

## 💡 L'Idea in 3 Righe

[Cosa vogliamo ottenere? Perché? Quale problema risolve?]

**Esempio**:
> Vogliamo che l'utente riceva avvisi vocali graduati quando si avvicina alle soglie di penalità (pescate e ricicli scarti), così può pianificare meglio le mosse e evitare penalità inaspettate. Attualmente non c'è nessun feedback preventivo.

---

## 🎭 Attori e Concetti

### Attori (Chi/Cosa Interagisce)

- **Utente**: [Ruolo, cosa fa nel sistema]
- **Sistema**: [Cosa gestisce, quali responsabilità]
- **[Altro Attore]**: [Se applicabile]

**Esempio**:
- **Utente**: Gioca a solitario, pesca carte, muove carte
- **Sistema**: Traccia mosse, calcola stato, fornisce feedback vocale

### Concetti Chiave (Cosa Esiste nel Sistema)

#### [Concetto 1]
- **Cos'è**: [Descrizione in termini umani, non tecnici]
- **Stati possibili**: [stato1, stato2, stato3]
- **Proprietà**: [Cosa lo caratterizza]

#### [Concetto 2]
- **Cos'è**: [...]
- **Stati possibili**: [...]
- **Proprietà**: [...]

**Esempio**:
#### Livello di Avviso
- **Cos'è**: Quanto dettagliato è il feedback vocale sulle soglie
- **Stati possibili**: Disattivato, Minimo, Bilanciato, Completo
- **Proprietà**: Determina quali messaggi vengono annunciati

#### Soglia di Penalità
- **Cos'è**: Punto in cui il sistema applica punti negativi
- **Stati possibili**: Non raggiunta, Prossima, Superata
- **Proprietà**: Valore numerico (es: 21 pescate)

### Relazioni Concettuali

[Diagramma ASCII semplice - chi usa chi, chi contiene chi]

```
Utente
  ↓ configura
Livello di Avviso
  ↓ determina quando annunciare
Soglia di Penalità
  ↓ influenza
Punteggio Finale
```

---

## 🎬 Scenari & Flussi

[Sintetizza 1–2 scenari principali; usa brevi liste numerate per il flusso.]

*Esempio: Utente pesca carta → sistema conta, verifica soglia, emette avviso.*

Aggiungi eventualmente uno scenario alternativo o un edge case, ma mantieni
la descrizione leggera: l'obiettivo è chiarire il flusso, non fornire uno
script dettagliato.

---

## 🔀 Stati e Transizioni

[Se utile, elenca brevemente gli stati principali e i trigger; altrimenti una
descrizione qualitativa basta.]

*Esempio:* `Sotto Soglia → Prossimo a Soglia → Sopra Soglia` con trigger "pesca
carta".

(Aggiungere diagramma ASCII solo se facilita la comprensione.)


---

## 🎮 Interazione Utente (UX Concettuale)

### Comandi/Azioni Disponibili

- **[Comando/Tasto/Gesto]**: 
  - Fa cosa? [Descrizione azione]
  - Quando disponibile? [Contesto/stato]
  - Feedback atteso: [Cosa sente/vede utente]

**Esempio**:
- **Tasto O (Opzioni)**:
  - Fa cosa? Apre menu configurazione, permette di cambiare livello avviso
  - Quando disponibile? Sempre, anche durante partita
  - Feedback atteso: "Menu opzioni. Opzione 9: Livello Avvisi, attualmente Bilanciato"

- **Tasto P (Pesca)**:
  - Fa cosa? Pesca carta dal mazzo riserve
  - Quando disponibile? Quando mazzo riserve non vuoto
  - Feedback atteso: "Hai pescato: 7 di Coppe" + eventuale avviso soglia

### Feedback Sistema

- **Quando [evento]**: Sistema comunica "[messaggio vocale esatto]"
- **Quando [errore]**: Sistema comunica "[messaggio errore]"

**Esempio**:
- **Quando utente pesca 20ª carta (livello Completo)**: "Attenzione: ancora una pescata e scatta la penalità di 1 punto!"
- **Quando utente pesca 21ª carta (livello Minimo)**: "Penalità attiva: -1 punto per pescata"
- **Quando livello avvisi = Disattivato**: Nessun messaggio vocale

### Navigazione Concettuale

[Come utente "si muove" nel sistema, scopre feature, cambia configurazione]

**Esempio**:
1. Utente apre menu opzioni (tasto O)
2. Naviga con frecce fino a "Opzione 9: Livello Avvisi"
3. Preme INVIO per ciclare: Disattivato → Minimo → Bilanciato → Completo
4. Sistema annuncia nuovo livello
5. Utente chiude opzioni (ESC), torna a partita
6. Prossima pescata usa nuovo livello avviso configurato

---

## 🤔 Domande & Decisioni

### Domande Aperte

- [ ] [Domanda irrisolta che blocca il design]
- [ ] [Scelta da fare tra opzione A e opzione B]
- [ ] [Comportamento non chiaro in scenario X]

**Esempio**:
- [ ] Gli avvisi dovrebbero interrompere altri messaggi TTS o accodarsi?
- [ ] Serve annuncio quando utente PASSA da una soglia all'altra senza azione diretta?
- [ ] Livello "Minimo" dovrebbe avvisare anche prima della soglia o solo dopo?

### Decisioni Prese

- ✅ **[Decisione]**: [Rationale in 1-2 righe]

**Esempio**:
- ✅ **Avvisi con interrupt=True**: Importante per accessibilità, soglie sono info critica
- ✅ **Livello default = Bilanciato**: Compromesso tra silenzio e verbosità eccessiva
- ✅ **Configurazione persistente**: Salvata in settings, utente non ri-configura ogni partita

### Assunzioni

- [Cosa diamo per scontato]

**Esempio**:
- Sistema TTS già funzionante e configurato
- Utente ha screen reader attivo (NVDA/JAWS)
- Comandi tastiera non in conflitto con altri binding

---

## 🎯 Opzioni Considerate

### Opzione A: [Nome Approccio]

**Descrizione**: [Come funzionerebbe questo approccio]

**Pro**: 
- ✅ [Vantaggio 1]
- ✅ [Vantaggio 2]

**Contro**:
- ❌ [Svantaggio 1]
- ❌ [Svantaggio 2]

---

### Opzione B: [Nome Approccio Alternativo]

**Descrizione**: [Come funzionerebbe]

**Pro/Contro**: [...]

---

### Scelta Finale

[Quale opzione abbiamo scelto? Perché?]

**Esempio**:
Scelto **Opzione A: 4 Livelli Graduati** invece di Opzione B (Solo ON/OFF) perché:
- Maggiore flessibilità per utenti con skill diversi
- Veterani possono disattivare, principianti hanno massima guida
- Sistema scalabile (facile aggiungere livelli futuri)

---

## ✅ Design Freeze Checklist

Questo design è pronto per la fase tecnica (PLAN) quando:

- [ ] Tutti gli scenari principali mappati
- [ ] Stati del sistema chiari e completi
- [ ] Flussi logici coprono tutti i casi d'uso
- [ ] Domande aperte risolte (o documentate come "da decidere in PLAN")
- [ ] UX interaction definita (comandi, feedback, navigazione)
- [ ] Nessun "buco logico" evidente
- [ ] Opzioni valutate e scelta finale motivata

**Next Step**: Creare `PLAN_[FEATURE].md` con decisioni API, architettura layer, file structure, testing strategy.

---

## 📝 Note di Brainstorming

[Spazio libero per idee, dubbi, "e se...", collegamenti ad altre feature]

**Esempio**:
- Potremmo estendere questo sistema anche ai ricicli scarti?
- In futuro: avvisi configurabili per singola soglia (granularità fine)

---

## 📚 Riferimenti Contestuali

### Feature Correlate
- [Nome feature esistente]: [Come si collega a questo design]

### Vincoli da Rispettare
- [Vincolo architetturale/UX esistente da mantenere]

**Esempio**:
### Feature Correlate
- **Sistema Punti v1.5.2**: Avvisi devono essere consistenti con logic scoring
- **Menu Opzioni esistente**: Nuova opzione deve integrarsi senza rompere navigazione

### Vincoli da Rispettare
- Tutti i messaggi TTS in italiano chiaro
- Navigazione solo tastiera (no mouse required)
- Pattern "ciclare con INVIO" già usato in altre opzioni

---

## 🎯 Risultato Finale Atteso (High-Level)

Una volta implementato, l'utente potrà:

✅ [Obiettivo utente 1 in linguaggio naturale]  
✅ [Obiettivo utente 2]  
✅ [Obiettivo utente 3]

**Esempio**:
✅ Configurare quanto dettagliati sono gli avvisi vocali (4 livelli)  
✅ Ricevere feedback preventivo prima di superare soglie penalità  
✅ Giocare senza distrazioni (modalità Disattivata) se esperto  
✅ Avere massima guida (modalità Completa) se principiante

---

**Fine Design Document**

---

## 🎯 Uso Template

### Quando Usare

✅ Brainstorming su nuova feature/fix  
✅ Mappare flussi logici prima di codificare  
✅ Decidere UX/interazione (COSA succede, non COME implementare)

❌ NON usare per decisioni API/architettura (usa `PLAN_*.md`)  
❌ NON usare per tracking implementazione (usa `TODO.md`)

### Workflow

DESIGN (concept, scenari utente) → PLAN (tecnico, API, testing) → TODO (operativo) → CHANGELOG (rilascio)

Usa linguaggio naturale, nessun codice. Focalizza su scenari utente e flussi logici. Passa a PLAN solo dopo Design Freeze (checklist sopra completata).

---

**Template Version**: v1.1 (ottimizzato -12.6%)  
**Data Creazione**: 2026-02-16  
**Ultima Modifica**: 2026-02-22  
**Autore**: AI Assistant + Nemex81  
**Filosofia**: "Diagrammi di flusso sulla lavagna" per programmatori non vedenti
