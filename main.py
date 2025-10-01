# bb84_stats.py
import random
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


def simulate_bb84_vector(n_bits=1000, eve_rate=0.0, channel_error=0.0, seed=None):
    rng = np.random.default_rng(seed)
    n = int(n_bits)
    alice_bits = rng.integers(0,2,size=n)
    alice_bases = rng.random(n) < 0.5   # True -> '+', False -> 'x'
    bob_bases = rng.random(n) < 0.5
    # Eve decisions
    eve_mask = rng.random(n) < float(eve_rate)
    eve_bases = rng.random(n) < 0.5
    # Eve measures (if intercept)
    eve_measures = np.where(eve_bases == alice_bases, alice_bits, rng.integers(0,2,size=n))
    # Bob result array
    bob_results = np.empty(n, dtype=int)
    # intercepted
    idx_int = np.where(eve_mask)[0]
    if idx_int.size > 0:
        bob_results[idx_int] = np.where(bob_bases[idx_int] == eve_bases[idx_int],
                                       eve_measures[idx_int],
                                       rng.integers(0,2,size=idx_int.size))
    # not intercepted
    idx_not = np.where(~eve_mask)[0]
    if idx_not.size > 0:
        bob_results[idx_not] = np.where(bob_bases[idx_not] == alice_bases[idx_not],
                                       alice_bits[idx_not],
                                       rng.integers(0,2,size=idx_not.size))
    # channel noise: flip bit with probability channel_error
    if channel_error > 0:
        flips = rng.random(n) < channel_error
        bob_results = np.where(flips, 1 - bob_results, bob_results)

    # sifting
    sift_mask = (alice_bases == bob_bases)
    sift_indices = np.nonzero(sift_mask)[0]
    num_sifted = sift_indices.size
    if num_sifted > 0:
        num_errors = np.sum(alice_bits[sift_mask] != bob_results[sift_mask])
        qber = num_errors / num_sifted
        shared_key = bob_results[sift_mask]  # or alice_bits[sift_mask], they should match except errors
    else:
        num_errors = 0
        qber = None
        shared_key = np.array([], dtype=int)

    return {
        'alice_bits': alice_bits,
        'alice_bases': alice_bases,
        'bob_bases': bob_bases,
        'bob_results': bob_results,
        'eve_mask': eve_mask,
        'eve_bases': eve_bases,
        'sift_indices': sift_indices,
        'num_sifted': num_sifted,
        'num_errors': num_errors,
        'qber': qber,
        'shared_key': shared_key
    }

# utility plotting can be added (omitted here for brevity; posso fornirla)

# Funzioni di plotting
def plot_example_run(res, show=True):
    """
    Disegna: (1) timeline dei bit Alice vs Bob (marcando i sifted)
             (2) barra con QBER e lunghezza chiave sifted.
    """
    n = len(res['alice_bits'])
    x = np.arange(n)

    plt.figure(figsize=(12, 6))

    # QBER e lunghezza chiave
    qber = res['qber']
    num_sifted = res['num_sifted']
    bars = plt.bar(['sifted length', 'errors', 'QBER (%)'],
                   [num_sifted, res['num_errors'], (qber * 100 if qber is not None else 0)])
    bars[2].set_color('C3')
    plt.ylim(0, max(num_sifted, 100, (qber * 100 if qber is not None else 0) + 10))

    plt.ylabel('count / percent')
    plt.grid(axis='y', linestyle='--', alpha=0.3)

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
            res = simulate_bb84_vector(n_bits=n_bits, eve_rate=r, seed=s)
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
    res = simulate_bb84_vector(n_bits=20, eve_rate=0.2, seed=42)
    print("n_bits:", 20)
    print("num_sifted:", res['num_sifted'])
    print("num_errors (on sifted):", res['num_errors'])
    print("QBER:", res['qber'])
    plot_example_run(res)

    # Curve QBER vs Eve
    qber_vs_eve_curve(n_bits=2000, seeds=8, eve_rates=np.linspace(0, 1, 11))
