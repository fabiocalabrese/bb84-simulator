# BB84 Quantum Key Distribution Simulator

Educational simulation of the **BB84** protocol in Python.  
This repository contains an implementation of the protocol with statistical simulations, channel noise, optional eavesdropping (Eve), and a simple **error correction** algorithm.

**Author:** Fabio Calabrese — `fabiocalabrese88@gmail.com`

---

## Objective

Demonstrate in practice:
- random generation of bits and bases by Alice,
- reception and measurement by Bob,
- optional eavesdropping by Eve,
- key sifting (keeping only bits with matching bases),
- estimation of the **QBER** (Quantum Bit Error Rate) via sampling,
- error correction of the sifted key using **block-based binary search**,
- estimation of **residual error after correction**,
- statistical analysis (mean and standard deviation) of QBER, key length, and residual error as a function of channel noise.

---

## Simulation method

The stochastic behavior is generated using NumPy (`np.random.*`):

- **Bits**: `np.random.randint(0,2,size=n)` generates Alice’s bits.  
- **Bases**: `np.random.randint(0,2,size=n)` generates the bases of Alice and Bob (and Eve when active).  
- **Channel noise**: `np.random.rand(len(bits)) < error_prob` generates boolean arrays to decide which bits to flip, implementing an independent error probability for each bit.  
- **Eavesdropping (Eve)**: if active, Eve chooses random bases;  
  - if the basis matches Alice’s, she measures correctly and resends the bit;  
  - if the basis does not match, she resends a random bit.  
- **Sifting**: Alice and Bob compare their bases and keep only the matching bits, producing the sifted key.  
- **QBER estimation**: a random sample of the sifted key is compared to estimate the fraction of errors.  
- **Error Correction**: the sifted key is divided into blocks; for each block, the parity is compared with Alice.  
  - If parities differ, a **binary search** is applied on the block to identify and correct single-bit errors.  
  - This operation is repeated for all blocks, producing Bob’s corrected key.  
- **Residual error**: calculated as the fraction of bits still mismatched after correction.

> The simulation is Monte Carlo–type: repeating multiple independent runs produces statistical estimates (mean and standard deviation) of QBER, key length, and residual error.

---

## Main files

- `bb84_alternative.py` — main script including:
  - random generation of bits/bases,
  - channel noise,
  - Eve interception,
  - key sifting,
  - QBER and key length calculation,
  - **block-based error correction**,
  - calculation of residual error after correction,
  - plotting results,
  - saving data to CSV.

---

## Saved output

At the end of the simulation, a CSV file is generated:

- **`bb84_results.csv`**  

Columns:
- `channel_error` — channel error probability  
- `mean_QBER_eve_off` — average QBER with Eve off  
- `std_QBER_eve_off` — QBER standard deviation (Eve off)  
- `mean_QBER_eve_on` — average QBER with Eve on  
- `std_QBER_eve_on` — QBER standard deviation (Eve on)  
- `mean_len_eve_off` — average sifted key length (Eve off)  
- `std_len_eve_off` — key length standard deviation (Eve off)  
- `mean_len_eve_on` — average sifted key length (Eve on)  
- `std_len_eve_on` — key length standard deviation (Eve on)  
- `mean_residual_eve_off` — average residual error after correction (Eve off)  
- `std_residual_eve_off` — standard deviation of residual error (Eve off)  
- `mean_residual_eve_on` — average residual error after correction (Eve on)  
- `std_residual_eve_on` — standard deviation of residual error (Eve on)  

---

## Main parameters

At startup, the script asks for (defaults used if input is invalid):

- `n` — number of bits per run (default: 2048)  
- `sample_size` — number of bits for error estimation (default: 1024)  
- `runs` — Monte Carlo runs per `channel_error` (default: 500)  
- `channel_errors` — channel error probability values (default: `0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2`)  
- `p_eve` — Eve's interception probability (default: 0.2)
---

## How to run

Clone the repository:
```bash
git clone https://github.com/fabiocalabrese/bb84-simulator.git
cd bb84-simulator
```
Install dependencies:
```
pip install numpy matplotlib
```
Launch the script:
```
python bb84_alternative.py
```

Follow the prompts to enter parameters, or use the default values.

## Generated plots

The script produces the following plots:

- **Average QBER vs channel noise**  
  (Eve off/on, with ± standard deviation bands, theoretical lines, and comparison with **residual error after correction**).  

- **Average sifted key length vs channel noise**  
  (Eve off/on, with ± standard deviation bands).  

- **Histograms of estimated QBER**  
  Distribution of errors for the last simulated `channel_error` value.

---

## Comments

Key observations from the simulation:

- Eve’s intervention on **100% of the key** produces a QBER of about **25%** even without channel noise.  
- Adding channel noise further increases the total QBER.  
- The **block-based error correction algorithm** works correctly, reducing residual error compared to the initial QBER.  
- To achieve higher error correction, it is necessary to **increase the number of blocks** used for block parity checks, i.e., create a finer division of the key.  
- However, increasing the number of blocks slightly exposes more information publicly, requiring subsequent **privacy amplification** to ensure the security of the final key.

