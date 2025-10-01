import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

# ---------------- FUNZIONI BB84 ----------------
def generate_bit(n):
    return np.random.randint(0, 2, size=n, dtype=np.int8)

def generate_basis(n):
    return np.random.randint(0, 2, size=n, dtype=np.int8)

def noisy_channel(bits, error_prob=0.0):
    flips = np.random.rand(len(bits)) < error_prob
    return np.bitwise_xor(bits, flips.astype(np.int8))

def interception(alice_bits, alice_basis, n, eve_active=True):
    if not eve_active:
        return alice_bits.copy(), alice_basis.copy()
    eve_basis = generate_basis(n)
    random_bits = np.random.randint(0, 2, size=n, dtype=np.int8)
    eve_measures = np.where(eve_basis == alice_basis, alice_bits, random_bits)
    return eve_measures, eve_basis

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

# ---------------- FUNZIONE DI SIMULAZIONE ----------------
def simulate_bb84(n, sample_size, eve_active=False, channel_error=0.0):
    alice_bits = generate_bit(n)
    alice_basis = generate_basis(n)

    transmitted_bits, sender_basis = interception(alice_bits, alice_basis, n, eve_active)
    bob_bits, bob_basis = bob_receive(transmitted_bits, sender_basis, n, error_prob=channel_error)

    alice_key, bob_key = sift_key(alice_bits, alice_basis, bob_bits, bob_basis)
    error_rate = sample_and_estimate_error(alice_key, bob_key, sample_size)
    return error_rate

# ---------------- SIMULAZIONE MULTIPLA ----------------
n = 4000
sample_size = 2000
runs = 1000
channel_errors = np.linspace(0, 0.2, 9)  # valori di errore del canale

# Salvo medie e deviazioni standard
error_mean_eve_off = []
error_std_eve_off = []
error_mean_eve_on = []
error_std_eve_on = []

# Salvo anche gli ultimi errori per gli istogrammi
errors_off_final = []
errors_on_final = []


for ce in channel_errors:
    # Eve disattiva
    errors_off = [simulate_bb84(n, sample_size, eve_active=False, channel_error=ce) for _ in range(runs)]
    error_mean_eve_off.append(np.mean(errors_off))
    error_std_eve_off.append(np.std(errors_off))
    if ce == channel_errors[-1]:
        errors_off_final = errors_off  # salva per istogramma

    # Eve attiva
    errors_on = [simulate_bb84(n, sample_size, eve_active=True, channel_error=ce) for _ in range(runs)]
    error_mean_eve_on.append(np.mean(errors_on))
    error_std_eve_on.append(np.std(errors_on))
    if ce == channel_errors[-1]:
        errors_on_final = errors_on  # salva per istogramma

# ---------------- LINE PLOT CON BANDA ±σ ----------------

plt.figure(figsize=(8, 5))

# Eve off
mean_off = np.array(error_mean_eve_off)
std_off = np.array(error_std_eve_off)
plt.plot(channel_errors, mean_off, marker='o', label="Eve off")
plt.fill_between(channel_errors, mean_off - std_off, mean_off + std_off, color='skyblue', alpha=0.3)

# Eve on
mean_on = np.array(error_mean_eve_on)
std_on = np.array(error_std_eve_on)
plt.plot(channel_errors, mean_on, marker='o', label="Eve on")
plt.fill_between(channel_errors, mean_on - std_on, mean_on + std_on, color='salmon', alpha=0.3)

plt.xlabel("Probabilità di errore del canale")
plt.ylabel("Errore medio stimato")
plt.title("Errore stimato nel BB84 in funzione del rumore del canale")
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
