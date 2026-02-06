# GUIDA IMPLEMENTAZIONE: Supporto Mazzo Napoletano Autentico (40 carte)

## PROBLEMA
Il mazzo napoletano attualmente genera 52 carte invece delle autentiche 40 carte.
Inoltre, ci sono bug critici nella verifica della vittoria che devono essere corretti.

## OBIETTIVO
Implementare il supporto corretto per il mazzo napoletano da 40 carte, eliminando 8, 9, 10 
e correggendo l'ordine delle figure: Regina (8), Cavallo (9), Re (10).

---

## BUG CRITICI IDENTIFICATI

### 1. Bug in `scr/game_table.py` - Metodo `verifica_vittoria()`
**Linea problematica:**
```python
for i in range(7, 10):  # BUG: controlla solo 3 pile invece di 4!
```

**Problema:** Il range(7, 10) controlla solo le pile 7, 8, 9 (3 pile) e IGNORA la pila 10 
(la quarta pila semi). Questo significa che il gioco può dichiarare vittoria anche se 
la quarta pila non è completa!

**Fix:** Deve essere `range(7, 11)` per controllare tutte e 4 le pile semi.

### 2. Valori Hardcoded
- Il controllo vittoria usa sempre 13 carte per seme (corretto per francesi, errato per napoletane)
- Le statistiche usano sempre 52 come totale carte
- I nomi dei semi nelle statistiche sono hardcoded come francesi

---

## MODIFICHE DA IMPLEMENTARE

### FILE 1: `scr/decks.py`

#### Modifica A: Classe `NeapolitanDeck` - Valori e Figure Corretti

**PRIMA (ERRATO - 52 carte):**
```python
VALUES = ["Asso", "2", "3", "4", "5", "6", "7", "8", "9", "10", "regina", "cavallo", "Re"]
FIGURE_VALUES = {"regina": 11, "cavallo": 12, "Re": 13, "Asso" : 1}
```

**DOPO (CORRETTO - 40 carte):**
```python
VALUES = ["Asso", "2", "3", "4", "5", "6", "7", "Regina", "Cavallo", "Re"]
FIGURE_VALUES = {"Regina": 8, "Cavallo": 9, "Re": 10, "Asso": 1}
```

**IMPORTANTE:** 
- Eliminati: "8", "9", "10"
- Cambiato "regina" → "Regina" (maiuscola per consistenza)
- Regina = 8, Cavallo = 9, Re = 10 (NON 11, 12, 13!)

#### Modifica B: Aggiungere metodo `get_total_cards()` a ENTRAMBE le classi

**In `NeapolitanDeck`:**
```python
def get_total_cards(self):
    """ Restituisce il numero totale di carte nel mazzo completo """
    return len(self.SUITES) * len(self.VALUES)  # 4 * 10 = 40
```

**In `FrenchDeck`:**
```python
def get_total_cards(self):
    """ Restituisce il numero totale di carte nel mazzo completo """
    return len(self.SUITES) * len(self.VALUES)  # 4 * 13 = 52
```

#### Modifica C: Aggiornare metodo `crea()` in `NeapolitanDeck`

Cambiare i riferimenti da "regina" a "Regina" nel controllo:
```python
if valore in ["Regina", "Cavallo", "Re", "Asso"]:  # Era: ["regina", "cavallo", "Re", "Asso"]
    carta.set_int_value(int(self.FIGURE_VALUES[valore]))
```

---

### FILE 2: `scr/game_table.py`

#### Modifica D: Fix Bug Critico in `verifica_vittoria()`

**PRIMA (BUGGY):**
```python
def verifica_vittoria(self):
    # verificare la vittoria controllando che le 4 pile semi siano composte da 13 carte
    for i in range(7, 10):  # BUG: controlla solo pile 7, 8, 9!
        if len(self.pile[i].carte) != 13:
            return False
    return True
```

**DOPO (CORRETTO E DINAMICO):**
```python
def verifica_vittoria(self):
    """ 
    Verifica la vittoria controllando che tutte le 4 pile semi siano complete.
    
    Per il mazzo francese: 13 carte per seme
    Per il mazzo napoletano: 10 carte per seme
    """
    # Ottieni il numero di carte per seme dal mazzo in uso
    carte_per_seme = len(self.mazzo.VALUES)  # 13 per francese, 10 per napoletano
    
    # Controlla tutte e 4 le pile semi (indici 7, 8, 9, 10)
    for i in range(7, 11):  # FIX: era range(7, 10) che saltava la pila 10!
        if len(self.pile[i].carte) != carte_per_seme:
            return False
    
    return True
```

**MOTIVAZIONE DEI FIX:**
1. `range(7, 11)` controlla TUTTE le 4 pile semi (7, 8, 9, 10)
2. `len(self.mazzo.VALUES)` rende dinamico il controllo:
   - Mazzo francese: VALUES ha 13 elementi → richiede 13 carte
   - Mazzo napoletano: VALUES ha 10 elementi → richiede 10 carte

---

### FILE 3: `scr/game_engine.py`

#### Modifica E: Metodo `aggiorna_statistiche_semi()`

**Trovare questa sezione (circa linea 565):**
```python
def aggiorna_statistiche_semi(self):
    # ... codice esistente ...
    
    # Un seme è completo se ha 13 carte (A-K)
    if num_carte == 13:
        self.semi_completati += 1
```

**SOSTITUIRE CON:**
```python
def aggiorna_statistiche_semi(self):
    """
    Aggiorna le statistiche delle carte nelle pile semi.
    
    Conta quante carte ci sono in ogni pila seme e quanti semi sono completi.
    Chiamato dopo ogni spostamento verso una pila seme.
    
    Effetti collaterali:
    - Aggiorna self.carte_per_seme[0-3]
    - Aggiorna self.semi_completati
    """
    if not self.is_game_running:
        return
    
    # Ottieni il numero di carte necessarie per completare un seme
    carte_per_seme_completo = len(self.tavolo.mazzo.VALUES)  # 13 o 10
    
    # Reset contatore semi completati per ricalcolo
    self.semi_completati = 0
    
    # Itera sulle 4 pile semi (indici 7-10)
    for i in range(4):
        pile_index = 7 + i  # Pile semi sono alle posizioni 7, 8, 9, 10
        pila_seme = self.tavolo.pile[pile_index]
        
        # Conta carte nella pila
        num_carte = pila_seme.get_len()
        self.carte_per_seme[i] = num_carte
        
        # Un seme è completo se ha tutte le carte (13 per francese, 10 per napoletano)
        if num_carte == carte_per_seme_completo:
            self.semi_completati += 1
```

#### Modifica F: Metodo `get_statistiche_semi()`

**Trovare questa sezione (circa linea 417):**
```python
def get_statistiche_semi(self):
    # ...
    nomi_semi = ["Cuori", "Quadri", "Fiori", "Picche"]
    # ...
    string += f"{nome_seme}: {num_carte} su 13 carte.  \n"
```

**SOSTITUIRE CON:**
```python
def get_statistiche_semi(self):
    """
    Vocalizza le statistiche correnti delle pile semi.
    
    Returns:
        str: Statistiche formattate per screen reader
    """
    if not self.is_game_running:
        return "Nessuna partita in corso.\n"
    
    # Nomi dinamici in base al mazzo
    nomi_semi_raw = self.tavolo.get_type_deck()  # ["cuori", ...] o ["bastoni", ...]
    nomi_semi = [seme.capitalize() for seme in nomi_semi_raw]
    carte_per_seme_completo = len(self.tavolo.mazzo.VALUES)  # 13 o 10
    
    string = "Statistiche pile semi:  \n"
    
    for i in range(4):
        num_carte = self.carte_per_seme[i]
        nome_seme = nomi_semi[i]
        string += f"{nome_seme}: {num_carte} su {carte_per_seme_completo} carte.  \n"
    
    string += f"\nHai completato {self.semi_completati} semi su 4.  \n"
    
    return string
```

#### Modifica G: Metodo `get_report_game()` - Calcolo Percentuale Dinamico

**Trovare ENTRAMBE le occorrenze (circa linee 448 e 492):**

**PRIMA:**
```python
percentuale = (totale_carte_semi / 52) * 100
string += f"Completamento totale: {totale_carte_semi}/52 carte ({percentuale:.1f}%).  \n"
```

**DOPO:**
```python
# Calcola totale carte del mazzo in uso
totale_carte_mazzo = self.tavolo.mazzo.get_total_cards()  # 52 o 40
percentuale = (totale_carte_semi / totale_carte_mazzo) * 100
string += f"Completamento totale: {totale_carte_semi}/{totale_carte_mazzo} carte ({percentuale:.1f}%).  \n"
```

**NOTA:** Questa modifica va applicata in DUE punti nel metodo:
1. Nella sezione "Partita terminata" (quando `not self.is_game_running`)
2. Nella sezione "Partita in corso" (quando `self.is_game_running`)

---

## TESTING CHECKLIST

Dopo l'implementazione, testare:

### Test Mazzo Napoletano
- [ ] Il mazzo genera esattamente 40 carte (4 semi × 10 valori)
- [ ] I valori sono: Asso, 2, 3, 4, 5, 6, 7, Regina, Cavallo, Re
- [ ] NON ci sono: 8, 9, 10, "regina" minuscola
- [ ] Regina vale 8, Cavallo vale 9, Re vale 10
- [ ] Nomi semi corretti: bastoni, coppe, denari, spade

### Test Verifica Vittoria
- [ ] Vittoria si verifica SOLO con tutte e 4 le pile semi complete
- [ ] Mazzo francese: richiede 13 carte per seme (52 totali)
- [ ] Mazzo napoletano: richiede 10 carte per seme (40 totali)
- [ ] Testare che con 3 pile complete e 1 incompleta NON si vinca

### Test Statistiche
- [ ] Le statistiche mostrano i nomi corretti dei semi per napoletane
- [ ] Il conteggio "X su Y carte" usa Y=10 per napoletane, Y=13 per francesi
- [ ] La percentuale di completamento usa 40 come denominatore per napoletane
- [ ] Il report finale mostra i valori corretti

### Test Gameplay
- [ ] Una partita con mazzo napoletano si può completare e vincere
- [ ] Il gioco distribuisce correttamente 28 carte nelle pile base (1+2+3+4+5+6+7)
- [ ] Rimangono 12 carte nel mazzo riserve (40 - 28 = 12)
- [ ] Le regole di impilamento funzionano correttamente

---

## IMPATTO DELLE MODIFICHE

### Cosa NON Cambia
- Le regole del solitario (impilamento tableau, pile semi)
- La logica di spostamento delle carte
- La distribuzione iniziale (sempre 28 carte nelle pile base)
- L'interfaccia utente

### Cosa Cambia
- Numero di carte nel mazzo napoletano: 52 → 40
- Valori delle figure napoletane: corretti da 11,12,13 a 8,9,10
- Vittoria con mazzo napoletano: 52 carte → 40 carte
- Carte nel mazzo riserve con napoletane: 24 → 12
- Statistiche e percentuali: dinamiche in base al mazzo

---

## NOTE TECNICHE

### Perché il mazzo napoletano ha 40 carte?
Le carte napoletane tradizionali eliminano gli 8, 9 e 10 da tutti i semi, 
mantenendo solo: Asso, 2-7, e le tre figure (Fante/Regina, Cavallo, Re).

### Perché le figure napoletane valgono 8, 9, 10?
Nel mazzo da 40 carte, le figure seguono direttamente il 7:
- 7 → Regina (8) → Cavallo (9) → Re (10)

Questo è diverso dal mazzo francese dove:
- 10 → Jack (11) → Queen (12) → King (13)

### Compatibilità
Entrambi i mazzi (francese e napoletano) devono coesistere nel codice.
L'utente può scegliere quale usare tramite il menu opzioni.

---

## RIEPILOGO FILE DA MODIFICARE

1. **scr/decks.py**
   - Classe `NeapolitanDeck`: VALUES, FIGURE_VALUES, metodo crea()
   - Classe `NeapolitanDeck`: aggiungere get_total_cards()
   - Classe `FrenchDeck`: aggiungere get_total_cards()

2. **scr/game_table.py**
   - Metodo `verifica_vittoria()`: fix bug range + logica dinamica

3. **scr/game_engine.py**
   - Metodo `aggiorna_statistiche_semi()`: logica dinamica
   - Metodo `get_statistiche_semi()`: nomi e conteggi dinamici
   - Metodo `get_report_game()`: percentuali dinamiche (2 punti)

---

## PRIORITÀ IMPLEMENTAZIONE

1. **CRITICA**: Fix bug `verifica_vittoria()` in game_table.py
2. **CRITICA**: Correzione VALUES e FIGURE_VALUES in decks.py
3. **ALTA**: Aggiunta metodo get_total_cards() in decks.py
4. **ALTA**: Aggiornamento statistiche dinamiche in game_engine.py
5. **MEDIA**: Testing completo di tutte le funzionalità

---

Fine della guida implementazione.
Versione: 1.0
Data: 2026-02-06
