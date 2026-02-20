# 🎨 Design Document - [Feature Name]

> **FASE: CONCEPT & FLOW DESIGN**  
> Nessuna decisione tecnica qui - solo logica e flussi concettuali  
> Equivalente a "diagrammi di flusso sulla lavagna"

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

### Scenario 1: [Nome Scenario Principale]

**Punto di partenza**: [Stato iniziale del sistema]

**Flusso**:

1. **Utente**: [Azione utente in linguaggio naturale]
   → **Sistema risponde**: [Cosa fa/mostra/comunica]
   
2. **Utente**: [Prossima azione]
   → **Sistema**: [Cambio stato/risposta]
   
3. **Utente**: [Continua...]
   → **Sistema**: [...]

**Punto di arrivo**: [Stato finale del sistema]

**Cosa cambia**: [Quali concetti sono stati modificati]

**Esempio**:
### Scenario 1: Utente Si Avvicina a Soglia Pescate

**Punto di partenza**: Utente ha pescato 19 carte, soglia penalità è 21

**Flusso**:
1. **Utente**: Preme tasto P per pescare
   → **Sistema**: Pesca carta, conta 20 pescate totali
   
2. **Sistema**: Verifica livello avviso (es: "Completo")
   → **Sistema**: Annuncia vocalmente "Attenzione: ancora una pescata e scatta la penalità!"
   
3. **Utente**: Ascolta avviso, decide se pescare ancora o cambiare strategia
   → **Sistema**: Attende prossima azione utente

**Punto di arrivo**: Utente informato, può decidere consapevolmente

**Cosa cambia**: Contatore pescate incrementato, avviso emesso una volta

---

### Scenario 2: [Nome Scenario Alternativo]

[Stesso formato del Scenario 1]

---

### Scenario 3: [Edge Case / Caso Limite]

**Cosa succede se**: [Condizione anomala o limite]

**Sistema dovrebbe**: [Comportamento atteso]

**Esempio**:
### Scenario 3: Avvisi Disattivati

**Cosa succede se**: Utente ha disattivato completamente gli avvisi

**Sistema dovrebbe**: Non emettere nessun annuncio vocale, ma continuare a tracciare soglie per calcolo punteggio

---

## 🔀 Stati e Transizioni

### Stati del Sistema

#### Stato A: [Nome Stato]
- **Descrizione**: [Cosa caratterizza questo stato]
- **Può passare a**: [Stato B, Stato C]
- **Trigger**: [Cosa causa il cambio stato]

#### Stato B: [Nome Stato]
- **Descrizione**: [...]
- **Può passare a**: [...]
- **Trigger**: [...]

**Esempio**:
#### Stato A: Sotto Soglia
- **Descrizione**: Contatore pescate < 21
- **Può passare a**: Prossimo a Soglia, Sopra Soglia
- **Trigger**: Azione "pesca carta"

#### Stato B: Prossimo a Soglia
- **Descrizione**: Contatore pescate = 20 (1 pescata prima della penalità)
- **Può passare a**: Sopra Soglia
- **Trigger**: Azione "pesca carta"

#### Stato C: Sopra Soglia
- **Descrizione**: Contatore pescate ≥ 21, penalità attiva
- **Può passare a**: Sopra Soglia Successiva (41)
- **Trigger**: Azione "pesca carta"

### Diagramma Stati (ASCII)

```
[Stato Iniziale: Sotto Soglia]
      ↓ (pesca carta, contatore < 20)
[Sotto Soglia] ←────────────┐
      ↓ (pesca carta, contatore = 20)  │
[Prossimo a Soglia]                 │ (nuova partita)
      ↓ (pesca carta, contatore = 21)  │
[Sopra Soglia] ───────────────┘
      ↓ (pesca carta, contatore ≥ 21)
[Sopra Soglia] (penalità continua)
```

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

**Next Step**: Creare `PLAN_[FEATURE].md` con:
- Decisioni API e architettura
- Layer assignment (Domain/Application/Infrastructure)
- File structure e code specifics
- Testing strategy dettagliata

---

## 📝 Note di Brainstorming

[Spazio libero per idee, dubbi, "e se...", collegamenti ad altre feature]

**Esempio**:
- Potremmo estendere questo sistema anche ai ricicli scarti?
- In futuro: avvisi configurabili per singola soglia (granularità fine)
- Collegamento con sistema punti: avvisi dovrebbero mostrare impatto punteggio?
- Accessibilità: testare con utenti NVDA per verbosità ottimale

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

## 🎯 Istruzioni Uso Template

### Quando Usare Questo Template

Usa questo template quando:
- ✅ Hai un'idea vaga di feature/fix da implementare
- ✅ Devi fare brainstorming su approcci alternativi
- ✅ Vuoi mappare flussi logici PRIMA di scrivere codice
- ✅ Serve "diagramma di flusso concettuale" accessibile
- ✅ Devi decidere UX/interazione senza ancora pensare all'implementazione

**NON usare questo template per**:
- ❌ Decisioni API e architettura (usa `PLAN_*.md`)
- ❌ Tracking implementazione (usa `TODO_*.md`)
- ❌ Documentazione feature già implementata (usa `ARCHITECTURE.md` o `API.md`)

### Workflow Completo

```
1. Idea vaga
   ↓
2. DESIGN_[FEATURE].md (questo template)
   - Brainstorming
   - Scenari utente
   - Flussi logici
   - Decisioni concettuali
   ↓ (Design Freeze)
3. PLAN_[FEATURE].md
   - API e architettura
   - Codice dettagliato
   - Testing strategy
   ↓ (Plan approvato)
4. TODO_[FEATURE].md
   - Tracking fase per fase
   - Checklist implementazione
   ↓ (Implementazione completa)
5. CHANGELOG.md + README.md
   - Documentazione user-facing
```

### Best Practices

✅ **DO**:
- Usa linguaggio naturale, non codice
- Disegna diagrammi ASCII per flussi
- Descrivi scenari come "storia utente"
- Focalizza su COSA succede, non COME implementare
- Includi edge cases e casi limite
- Valuta più opzioni prima di decidere

❌ **DON'T**:
- Non scrivere nomi di classi/metodi (troppo presto)
- Non decidere layer architetturali (viene in PLAN)
- Non pensare a file structure (troppo tecnico)
- Non saltare scenari "noiosi" (spesso nascondono complessità)
- Non decidere senza motivare (rationale sempre)

### Segnali che Design è Pronto

✅ Puoi spiegare la feature a qualcuno in 2 minuti  
✅ Scenari coprono tutti i casi d'uso principali  
✅ Non ci sono "buchi logici" evidenti  
✅ Decisioni chiave prese e motivate  
✅ UX chiara (comandi, feedback, navigazione)  
✅ Stati sistema mappati completamente

**Se manca anche solo uno → Design ancora DRAFT**

---

**Template Version**: v1.0  
**Data Creazione**: 2026-02-16  
**Autore**: AI Assistant + Nemex81  
**Filosofia**: "Diagrammi di flusso sulla lavagna" per programmatori non vedenti
