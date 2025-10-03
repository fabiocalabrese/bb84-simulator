# BB84 Quantum Key Distribution Simulator

Simulazione didattica del protocollo **BB84** in Python.  
Questo repository contiene un’implementazione del protocollo con simulazioni statistiche, introduzione di rumore di canale, la possibilità di attivare un intercettatore (Eve), e un semplice algoritmo di **error correction**.

**Autore:** Fabio Calabrese — `fabiocalabrese88@gmail.com`

---

## Obiettivo

Mostrare in modo pratico:
- la generazione casuale di bit e basi da parte di Alice,
- la ricezione e misurazione da parte di Bob,
- l’intercettazione di Eve (opzionale),
- il sifting della chiave (conservando solo i bit con basi coincidenti),
- la stima del **QBER** (Quantum Bit Error Rate) tramite campionamento,
- la correzione degli errori nella chiave siftata tramite **binary search a blocchi**,
- la stima dell’**errore residuo dopo correzione**,
- l’analisi statistica (media e deviazione standard) di QBER, lunghezza chiave e errore residuo in funzione del rumore di canale.

---

## Metodo e criteri di simulazione

Il comportamento stocastico è generato con NumPy (`np.random.*`):

- **Bit**: `np.random.randint(0,2,size=n)` genera i bit di Alice.  
- **Basi**: `np.random.randint(0,2,size=n)` genera le basi di Alice e Bob (e di Eve quando attiva).  
- **Rumore di canale**: `np.random.rand(len(bits)) < error_prob` genera array booleani per decidere quali bit flippare, implementando una probabilità indipendente di errore per ciascun bit.  
- **Intercettazione (Eve)**: se attiva, Eve sceglie basi casuali;  
  - se la base coincide con quella di Alice, misura correttamente e reinvia il bit;  
  - se la base non coincide, reinvia un bit casuale.  
- **Sifting**: Alice e Bob confrontano le basi e conservano solo i bit coincidenti, producendo la chiave siftata.  
- **Stima del QBER**: un campione casuale della chiave siftata viene confrontato per stimare la frazione di errori.  
- **Error Correction**: la chiave siftata viene suddivisa in blocchi; per ciascun blocco si confronta la parità con Alice.  
  - Se le parità differiscono, viene applicata una **ricerca binaria** sul blocco fino a identificare e correggere bit singoli errati.  
  - L’operazione viene ripetuta per tutti i blocchi, producendo la chiave corretta di Bob.  
- **Errore residuo**: calcolato come la frazione di bit ancora discordanti dopo la correzione.

> La simulazione è di tipo Monte Carlo: ripetendo più run indipendenti si ottengono stime statistiche (medie e deviazioni standard) di QBER, lunghezza chiave e errore residuo.

---

## File principali

- `bb84_alternative.py` — script principale con:
  - generazione casuale dei bit/basi,
  - rumore di canale,
  - intercettazione di Eve,
  - sifting della chiave,
  - calcolo QBER e lunghezza chiave,
  - **correzione degli errori a blocchi**,
  - calcolo errore residuo dopo correzione,
  - plotting dei risultati,
  - salvataggio dei dati in CSV.  

---

## Output salvato

Alla fine della simulazione viene generato un file CSV:

- **`bb84_results.csv`**  

Colonne:
- `channel_error` — probabilità di errore del canale  
- `mean_QBER_eve_off` — QBER medio con Eve disattiva  
- `std_QBER_eve_off` — deviazione standard QBER (Eve off)  
- `mean_QBER_eve_on` — QBER medio con Eve attiva  
- `std_QBER_eve_on` — deviazione standard QBER (Eve on)  
- `mean_len_eve_off` — lunghezza media chiave siftata (Eve off)  
- `std_len_eve_off` — deviazione standard della lunghezza (Eve off)  
- `mean_len_eve_on` — lunghezza media chiave siftata (Eve on)  
- `std_len_eve_on` — deviazione standard della lunghezza (Eve on)  
- `mean_residual_eve_off` — errore residuo medio dopo correzione (Eve off)  
- `std_residual_eve_off` — deviazione standard dell’errore residuo (Eve off)  
- `mean_residual_eve_on` — errore residuo medio dopo correzione (Eve on)  
- `std_residual_eve_on` — deviazione standard dell’errore residuo (Eve on)  

---

## Parametri principali

All’avvio, lo script richiede (con default se input non valido):

- `n` — numero di bit per run (default: 100)  
- `sample_size` — numero di bit per stimare l’errore (default: 10)  
- `runs` — numero di run Monte Carlo per ciascun `channel_error` (default: 500)  
- `channel_errors` — valori di probabilità di errore del canale (default: `0,0.01,0.05,0.1,0.2`)  

Eve è attiva **sempre** nella parte “Eve on” della simulazione; la comparazione avviene fra scenario Eve off ed Eve on.

---
## Come eseguire

1. Clona il repository:
```bash
git clone https://github.com/fabiocalabrese/bb84-simulator.git
cd bb84-simulator
```
Installa le dipendenze:
```
pip install numpy matplotlib
```

Lancia lo script:
```
python bb84_alternative.py
```

Segui le richieste per l’inserimento dei parametri oppure lascia che il programma usi i valori di default.

## Grafici generati

Lo script produce i seguenti grafici a video:

- **QBER medio vs rumore di canale**  
  (Eve off/on, con bande ± deviazione standard, linee teoriche, e confronto con **errore residuo dopo correzione**).  

- **Lunghezza media della chiave siftata vs rumore di canale**  
  (Eve off/on, con bande ± deviazione standard).  

- **Istogrammi del QBER stimato**  
  Distribuzione degli errori sull’ultimo valore di `channel_error` simulato.  

---

## Commenti

Dalla simulazione si possono notare i seguenti punti chiave:

- L’intervento di Eve al **100% della chiave** produce un QBER di circa **25%** anche senza rumore di canale.  
- L’inclusione del rumore di canale aumenta ulteriormente il QBER totale.  
- L’algoritmo di **error correction a blocchi** funziona correttamente: riduce l’errore residuo rispetto al QBER iniziale.  
- Per ottenere una maggiore correzione degli errori, è necessario **aumentare il numero di blocchi** soggetti alla block parity, ovvero creare una suddivisione più fine della chiave.  
- Tuttavia, aumentare il numero di blocchi espone maggiormente l’informazione pubblica e quindi richiede l’uso successivo di **privacy amplification** per garantire la sicurezza della chiave finale.
