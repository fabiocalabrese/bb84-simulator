import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import csv


def bb84_banner():
    print("\n=== BB84 Quantum Key Distribution Simulator ===")
    print("A cura di Fabio Calabrese (fabiocalabrese88@gmail.com)\n")


# ---------------- FUNZIONI BB84 ----------------
def generate_bit(n):
    return np.random.randint(0, 2, size=n, dtype=np.int8)

def generate_basis(n):
    return np.random.randint(0, 2, size=n, dtype=np.int8)

def noisy_channel(bits, error_prob=0.0):
    flips = np.random.rand(len(bits)) < error_prob
    return np.bitwise_xor(bits, flips.astype(np.int8))

def interception_partial(alice_bits, alice_basis, n, eve_active=True, p_eve=1.0):
    """
    Intercetta solo una frazione dei bit (intercept-resend).
    - p_eve: frazione intercettata (0.0..1.0)
    Restituisce: (transmitted_bits, sender_basis)
    """
    if not eve_active or p_eve <= 0:
        return alice_bits.copy(), alice_basis.copy()

    # maschera di intercettazione (True = Eve intercetta)
    mask = np.random.rand(n) < p_eve
    eve_basis = generate_basis(n)
    transmitted = alice_bits.copy()
    rand_bits = np.random.randint(0, 2, size=n, dtype=np.int8)

    idx = np.where(mask)[0]
    if idx.size > 0:
        same_base = eve_basis[idx] == alice_basis[idx]
        transmitted[idx[same_base]] = alice_bits[idx[same_base]]
        transmitted[idx[~same_base]] = rand_bits[idx[~same_base]]

    sender_basis = alice_basis.copy()
    sender_basis[mask] = eve_basis[mask]

    return transmitted, sender_basis

def bob_receive(sent_bits, sender_basis, n, error_prob=0.0):
    bob_basis = generate_basis(n)
    random_bits = np.random.randint(0, 2, size=n, dtype=np.int8)
    bob_measure = np.where(bob_basis == sender_basis, sent_bits, random_bits)
    bob_measure = noisy_channel(bob_measure, error_prob)
    return bob_measure, bob_basis

def sift_key(alice_bits, alice_basis, bob_bits, bob_basis):
    mask = alice_basis == bob_basis
    alice_key = alice_bits[mask]
    bob_key = bob_bits[mask]
    return alice_key, bob_key

def sample_and_estimate_error(alice_key, bob_key, sample_size):
    n = len(alice_key)
    if n <= sample_size:
        sample_size = n // 2
    permutation = np.random.permutation(n)
    alice_perm = alice_key[permutation]
    bob_perm = bob_key[permutation]
    alice_sample = alice_perm[:sample_size]
    bob_sample = bob_perm[:sample_size]
    errors = np.sum(alice_sample != bob_sample)
    return errors / sample_size if sample_size > 0 else 0

def binary_search_error(alice_block, bob_block):
    """
    Ricerca binaria dell'errore in un blocco.
    Restituisce il bob_block corretto (modificato localmente).
    """
    n = len(alice_block)
    if n == 0:
        return bob_block

    # Se le parità coincidono, non ci sono errori (o pari numero di errori)
    if np.bitwise_xor.reduce(alice_block) == np.bitwise_xor.reduce(bob_block):
        return bob_block

    # Se siamo arrivati ad un singolo bit, correggilo
    if n == 1:
        bob_block[0] ^= 1
        return bob_block

    # Dividi a metà e controlla la parità della prima metà
    mid = n // 2
    alice_left, bob_left = alice_block[:mid], bob_block[:mid]
    alice_right, bob_right = alice_block[mid:], bob_block[mid:]

    if np.bitwise_xor.reduce(alice_left) != np.bitwise_xor.reduce(bob_left):
        # L'errore è nella metà sinistra
        corrected_left = binary_search_error(alice_left, bob_left)
        return np.concatenate((corrected_left, bob_right))
    else:
        # L'errore è nella metà destra
        corrected_right = binary_search_error(alice_right, bob_right)
        return np.concatenate((bob_left, corrected_right))


def block_error_correction(alice_key, bob_key, num_blocks=4):
    """
    Divide la chiave in num_blocks blocchi e applica la ricerca binaria
    per correggere i blocchi con parità discordante.
    Restituisce la chiave di Bob corretta.
    """
    n = len(alice_key)
    corrected_bob = bob_key.copy()
    block_size = max(1, n // num_blocks)

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        alice_block = alice_key[start:end]
        bob_block = corrected_bob[start:end]

        # Se le parità differiscono, cerca e correggi
        if np.bitwise_xor.reduce(alice_block) != np.bitwise_xor.reduce(bob_block):
            corrected_block = binary_search_error(alice_block, bob_block)
            corrected_bob[start:end] = corrected_block

    return corrected_bob



# ---------------- FUNZIONE DI SIMULAZIONE ----------------
def simulate_bb84(n, sample_size, eve_active=False, channel_error=0.0, p_eve=1.0):
    alice_bits = generate_bit(n)
    alice_basis = generate_basis(n)

    transmitted_bits, sender_basis = interception_partial(alice_bits, alice_basis, n,
                                                          eve_active=eve_active, p_eve=p_eve)
    bob_bits, bob_basis = bob_receive(transmitted_bits, sender_basis, n, error_prob=channel_error)

    alice_key, bob_key = sift_key(alice_bits, alice_basis, bob_bits, bob_basis)
    error_rate = sample_and_estimate_error(alice_key, bob_key, sample_size)
    key_length = len(alice_key)


    corrected_bob_key = block_error_correction(alice_key, bob_key, num_blocks=20)
    if len(alice_key) > 0:
        residual_error = np.mean(alice_key != corrected_bob_key)
    else:
        residual_error = 0

    return error_rate, key_length, residual_error


# ---------------- SIMULAZIONE MULTIPLA ----------------
bb84_banner()

try:
    n = int(input("Inserisci il numero di bit per run (es. 100): "))
    sample_size = int(input("Inserisci la dimensione del campione per stima errore (es. 10): "))
    runs = int(input("Inserisci il numero di run per ciascun channel_error (es. 500): "))
    channel_errors_input = input("Inserisci i valori di channel_error separati da virgola (es. 0,0.01,0.05,0.1,0.2): ")
    channel_errors = [float(x.strip()) for x in channel_errors_input.split(",")]
    p_eve = float(input("Inserisci la frazione di intercettazione di Eve (es. 1.0 = 100%, 0.5 = 50%): "))
except ValueError:
    print("Input non valido, si utilizzano parametri di default.")
    n = 2048
    sample_size = 1024
    runs = 500
    channel_errors = [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2]
    p_eve = 0

print(f"\nSimulazione pronta con i seguenti parametri:")
print(f"- Numero di bit: {n}")
print(f"- Dimensione campione: {sample_size}")
print(f"- Numero di run: {runs}")
print(f"- Channel errors: {channel_errors}")
print(f"- Frazione intercettata da Eve: {p_eve}")

# Risultati (errori e lunghezze)
error_mean_eve_off, error_std_eve_off = [], []
error_mean_eve_on, error_std_eve_on = [], []
length_mean_eve_off, length_std_eve_off = [], []
length_mean_eve_on, length_std_eve_on = [], []
residual_mean_eve_off, residual_std_eve_off = [], []
residual_mean_eve_on, residual_std_eve_on = [], []

for ce in channel_errors:
    # Eve OFF
    results_off = [simulate_bb84(n, sample_size, eve_active=False, channel_error=ce, p_eve=p_eve) for _ in range(runs)]
    errors_off = [r[0] for r in results_off]
    lengths_off = [r[1] for r in results_off]
    residuals_off = [r[2] for r in results_off]
    error_mean_eve_off.append(np.mean(errors_off))
    error_std_eve_off.append(np.std(errors_off))
    length_mean_eve_off.append(np.mean(lengths_off))
    length_std_eve_off.append(np.std(lengths_off))
    residual_mean_eve_off.append(np.mean(residuals_off))
    residual_std_eve_off.append(np.std(residuals_off))
    if ce == channel_errors[-1]:
        errors_off_final = errors_off

    # Eve ON
    results_on = [simulate_bb84(n, sample_size, eve_active=True, channel_error=ce, p_eve=p_eve) for _ in range(runs)]
    errors_on = [r[0] for r in results_on]
    lengths_on = [r[1] for r in results_on]
    residuals_on = [r[2] for r in results_on]
    error_mean_eve_on.append(np.mean(errors_on))
    error_std_eve_on.append(np.std(errors_on))
    length_mean_eve_on.append(np.mean(lengths_on))
    length_std_eve_on.append(np.std(lengths_on))
    residual_mean_eve_on.append(np.mean(residuals_on))
    residual_std_eve_on.append(np.std(residuals_on))
    if ce == channel_errors[-1]:
        errors_on_final = errors_on


# ---------------- GRAFICO 1: QBER ----------------
plt.figure(figsize=(8, 5))

# QBER stimato (prima della correzione)
mean_off = np.array(error_mean_eve_off)
std_off = np.array(error_std_eve_off)
plt.plot(channel_errors, mean_off, marker='o', label="QBER Eve off (prima correzione)")
plt.fill_between(channel_errors, mean_off - std_off, mean_off + std_off, color='skyblue', alpha=0.3)

mean_on = np.array(error_mean_eve_on)
std_on = np.array(error_std_eve_on)
plt.plot(channel_errors, mean_on, marker='o', label="QBER Eve on (prima correzione)")
plt.fill_between(channel_errors, mean_on - std_on, mean_on + std_on, color='salmon', alpha=0.3)

# Errore residuo (dopo correzione)
mean_res_off = np.array(residual_mean_eve_off)
std_res_off = np.array(residual_std_eve_off)
plt.plot(channel_errors, mean_res_off, marker='s', linestyle='--', label="Residuo Eve off (dopo correzione)")

mean_res_on = np.array(residual_mean_eve_on)
std_res_on = np.array(residual_std_eve_on)
plt.plot(channel_errors, mean_res_on, marker='s', linestyle='--', label="Residuo Eve on (dopo correzione)")

# Linee di riferimento teoriche
plt.plot(channel_errors, channel_errors, 'k--', label="QBER teorico (rumore)")
plt.axhline(0.25 * p_eve, color='gray', linestyle=':', label=f"QBER teorico Eve ({p_eve*100:.0f}%)")

plt.xlabel("Probabilità di errore del canale")
plt.ylabel("Errore (QBER o residuo)")
plt.title("QBER prima e dopo correzione nel BB84")
plt.grid(True)
plt.legend()
plt.show()


# ---------------- GRAFICO 2: LUNGHEZZA CHIAVE ----------------
plt.figure(figsize=(8, 5))

mean_len_off = np.array(length_mean_eve_off)
std_len_off = np.array(length_std_eve_off)
plt.plot(channel_errors, mean_len_off, marker='o', label="Eve off")
plt.fill_between(channel_errors, mean_len_off - std_len_off, mean_len_off + std_len_off, color='skyblue', alpha=0.3)

mean_len_on = np.array(length_mean_eve_on)
std_len_on = np.array(length_std_eve_on)
plt.plot(channel_errors, mean_len_on, marker='o', label="Eve on")
plt.fill_between(channel_errors, mean_len_on - std_len_on, mean_len_on + std_len_on, color='salmon', alpha=0.3)

plt.xlabel("Probabilità di errore del canale")
plt.ylabel("Lunghezza media chiave siftata")
plt.title("Lunghezza chiave residua in funzione del rumore del canale")
plt.grid(True)
plt.legend()
plt.show()


# ---------------- ISTOGRAMMI FINALI ----------------
plt.figure(figsize=(12,5))

plt.subplot(1,2,1)
plt.hist(errors_off_final, bins=30, color='skyblue', edgecolor='black')
plt.title("Distribuzione errore Eve off (c.e = 0.2)")
plt.xlabel("Errore stimato")
plt.ylabel("Frequenza")

plt.subplot(1,2,2)
plt.hist(errors_on_final, bins=30, color='salmon', edgecolor='black')
plt.title("Distribuzione errore Eve on (c.e = 0.2)")
plt.xlabel("Errore stimato")
plt.ylabel("Frequenza")

plt.tight_layout()
plt.show()

"""
# ---------------- SALVATAGGIO RISULTATI ----------------
with open("bb84_results.csv", mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["channel_error",
                     "mean_QBER_eve_off", "std_QBER_eve_off",
                     "mean_QBER_eve_on", "std_QBER_eve_on",
                     "mean_len_eve_off", "std_len_eve_off",
                     "mean_len_eve_on", "std_len_eve_on"])
    for i, ce in enumerate(channel_errors):
        writer.writerow([ce,
                         error_mean_eve_off[i], error_std_eve_off[i],
                         error_mean_eve_on[i], error_std_eve_on[i],
                         length_mean_eve_off[i], length_std_eve_off[i],
                         length_mean_eve_on[i], length_std_eve_on[i]])

print("\nRisultati salvati in 'bb84_results.csv'.")

"""