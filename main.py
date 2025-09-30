# bb84_stats.py
import random
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


def simulate_bb84(n_bits=1000, eve_rate=0.0, seed=None):
    """
    Simula il protocollo BB84:
    - n_bits: numero di qubit inviati da Alice
    - eve_rate: frazione [0..1] dei qubit intercettati da Eve
    - seed: seme per riproducibilità (opzionale)

    Restituisce un dizionario con tutti i vettori e le statistiche:
    {
      'alice_bits', 'alice_bases', 'bob_bases', 'bob_results',
      'intercepted_flags', 'sifted_indices', 'num_sifted',
      'num_errors', 'qber', 'shared_key'
    }
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    # Helper
    rand_bit = lambda: 0 if random.random() < 0.5 else 1
    rand_basis = lambda: '+' if random.random() < 0.5 else 'x'

    alice_bits = []
    alice_bases = []
    bob_bases = []
    bob_results = []
    intercepted_flags = []  # True se Eve ha intercettato quel qubit
    eve_bases = [None] * n_bits
    eve_measures = [None] * n_bits

    for i in range(n_bits):
        # Alice genera bit + base
        a_bit = rand_bit()
        a_basis = rand_basis()
        alice_bits.append(a_bit)
        alice_bases.append(a_basis)

        # Decide se Eve intercetta questo qubit
        intercepted = (random.random() < eve_rate)
        intercepted_flags.append(intercepted)

        # Bob sceglie la base
        b_basis = rand_basis()
        bob_bases.append(b_basis)

        # Caso con Eve
        if intercepted:
            e_basis = rand_basis()
            eve_bases[i] = e_basis
            # Eve misura: se sceglie la stessa base di Alice prende il bit corretto,
            # altrimenti ottiene bit casuale
            if e_basis == a_basis:
                e_val = a_bit
            else:
                e_val = rand_bit()
            eve_measures[i] = e_val
            # Eve reinvia un qubit preparato nella base e_val con base e_basis
            # Bob misura il qubit reinviato:
            if b_basis == e_basis:
                bob_val = e_val
            else:
                bob_val = rand_bit()
        else:
            # Senza Eve: Bob misura il qubit originale
            if b_basis == a_basis:
                bob_val = a_bit
            else:
                bob_val = rand_bit()

        bob_results.append(bob_val)

    # Sifting: indici in cui alice_bases == bob_bases
    sifted_indices = [i for i in range(n_bits) if alice_bases[i] == bob_bases[i]]
    num_sifted = len(sifted_indices)

    # Errori: tra alice_bits e bob_results su indici sifted
    num_errors = 0
    shared_key = []
    for i in sifted_indices:
        if alice_bits[i] != bob_results[i]:
            num_errors += 1
        else:
            pass
        shared_key.append(bob_results[i])

    qber = (num_errors / num_sifted) if num_sifted > 0 else None

    return {
        'alice_bits': np.array(alice_bits),
        'alice_bases': np.array(alice_bases),
        'bob_bases': np.array(bob_bases),
        'bob_results': np.array(bob_results),
        'intercepted_flags': np.array(intercepted_flags),
        'eve_bases': np.array(eve_bases),
        'eve_measures': np.array(eve_measures),
        'sifted_indices': np.array(sifted_indices),
        'num_sifted': num_sifted,
        'num_errors': num_errors,
        'qber': qber,
        'shared_key': np.array(shared_key)
    }


# Funzioni di plotting
def plot_example_run(res, show=True):
    """
    Disegna: (1) timeline dei bit Alice vs Bob (marcando i sifted)
             (2) barra con QBER e lunghezza chiave sifted.
    """
    n = len(res['alice_bits'])
    x = np.arange(n)

    plt.figure(figsize=(12, 6))

    # subplot 1: Alice & Bob values, highlight sifted and errors
    ax1 = plt.subplot(2, 1, 1)
    ax1.set_title('Alice bits (alto) vs Bob results (basso) — punti sifted evidenziati')
    # offset y per disegnare Alice sopra e Bob sotto
    ax1.scatter(x, res['alice_bits'] + 1.2, c='C0', label='Alice bit', s=20)
    ax1.scatter(x, res['bob_results'] - 1.2, c='C1', label='Bob result', s=20)

    sifted = res['sifted_indices']
    # Mark sifted indices with vertical grey lines and highlight mismatches in red
    for i in sifted:
        ax1.axvline(i, color='#e6e6e6', linewidth=0.5)
    # mismatches among sifted
    mismatches = [i for i in sifted if res['alice_bits'][i] != res['bob_results'][i]]
    matches = [i for i in sifted if res['alice_bits'][i] == res['bob_results'][i]]

    ax1.scatter(matches, res['alice_bits'][matches] + 1.2, facecolors='none', edgecolors='green', s=80, linewidths=1.5,
                label='sifted match')
    ax1.scatter(mismatches, res['alice_bits'][mismatches] + 1.2, facecolors='none', edgecolors='red', s=80,
                linewidths=1.5, label='sifted mismatch')

    ax1.set_yticks([-1.2, 0, 1, 1.2])
    ax1.set_yticklabels(['Bob=0', '', '', 'Alice=1'])
    ax1.set_xlim(-1, n)
    ax1.legend(loc='upper right')

    # subplot 2: QBER e lunghezza chiave
    ax2 = plt.subplot(2, 1, 2)
    qber = res['qber']
    num_sifted = res['num_sifted']
    bars = ax2.bar(['sifted length', 'errors', 'QBER (%)'],
                   [num_sifted, res['num_errors'], (qber * 100 if qber is not None else 0)])
    bars[2].set_color('C3')
    ax2.set_ylim(0, max(num_sifted, 100, (qber * 100 if qber is not None else 0) + 10))

    ax2.set_ylabel('count / percent')
    ax2.grid(axis='y', linestyle='--', alpha=0.3)

    plt.tight_layout()
    if show:
        plt.show()


def qber_vs_eve_curve(n_bits=2000, seeds=5, eve_rates=None):
    """
    Simula più volte per ogni eve_rate e mostra QBER medio ± std.
    """
    if eve_rates is None:
        eve_rates = np.linspace(0, 1, 11)  # da 0 a 1
    means = []
    stds = []
    for r in eve_rates:
        qbers = []
        for s in range(seeds):
            res = simulate_bb84(n_bits=n_bits, eve_rate=r, seed=s)
            qbers.append(res['qber'] if res['qber'] is not None else 0)
        qbers = np.array(qbers)
        means.append(qbers.mean())
        stds.append(qbers.std())
    means = np.array(means);
    stds = np.array(stds)

    plt.figure(figsize=(8, 5))
    plt.errorbar(eve_rates, means * 100, yerr=stds * 100, marker='o', capsize=4)
    # linea teorica attesa: QBER ≈ eve_rate * 0.25 (se Eve misura sempre in base casuale)
    theo = 0.25 * np.array(eve_rates)
    plt.plot(eve_rates, theo * 100, '--', color='gray', label='teoria: QBER = 0.25 * eve_rate')
    plt.xlabel('Eve interception rate')
    plt.ylabel('QBER (%)')
    plt.title('QBER in funzione della probabilità di intercettazione (media su runs)')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()


# --- script di esempio per eseguire tutto ---
if __name__ == "__main__":
    # Esempio singola run
    res = simulate_bb84(n_bits=500, eve_rate=0.2, seed=42)
    print("n_bits:", 500)
    print("num_sifted:", res['num_sifted'])
    print("num_errors (on sifted):", res['num_errors'])
    print("QBER:", res['qber'])
    plot_example_run(res)

    # Curve QBER vs Eve
    qber_vs_eve_curve(n_bits=2000, seeds=8, eve_rates=np.linspace(0, 1, 11))
