# BB84 Quantum Key Distribution Simulator

Simulazione del protocollo **BB84** in Python.  
A cura di **Fabio Calabrese** — fabiocalabrese88@gmail.com

---

## Contenuti del repository

- `bb84_alternative.py` — codice Python principale per la simulazione BB84.
- `.gitignore` — ignora file temporanei, IDE e virtual environment.
- README.md — documentazione del progetto.

> Nota: al momento il repository contiene solo il codice principale. In futuro possono essere aggiunti notebook, output CSV o grafici.

---

## Descrizione del progetto

Questo progetto simula il protocollo di distribuzione quantistica delle chiavi **BB84**.  
Permette di:

- Generare bit casuali per Alice  
- Generare basi casuali per Alice e Bob  
- Simulare l’intercettazione di Eve (on/off, parziale o totale)  
- Effettuare **sifting** della chiave  
- Stimare il tasso di errore su un campione di bit  
- Analizzare l’effetto di diversi livelli di rumore del canale  
- Preparare output per grafici o salvataggio dei dati

---

## Requisiti

- Python 3.10+  
- Librerie:
  ```
  numpy
  matplotlib
  ```
Opzionale, per notebook futuri:
```
jupyterlab
pandas
```
Puoi installare tutto con:

```bash
pip install numpy matplotlib
# opzionale:
pip install jupyterlab pandas
```

Esecuzione

Clona il repository:
```
git clone https://github.com/fabiocalabrese/bb84-simulator.git
cd bb84-simulator
```


Esegui lo script Python:
```
python bb84_alternative.py
```

Modifica i parametri all’inizio del file (n, sample_size, runs, eve_active, channel_error) per personalizzare la simulazione.
