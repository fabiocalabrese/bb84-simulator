import numpy as np

# ---------------- FUNZIONI BASE ----------------
def generate_bit(n):
    """Genera n bit casuali 0 o 1"""
    return np.random.randint(0, 2, size=n, dtype=np.int8)

def generate_basis(n):
    """Genera n basi casuali 0 o 1"""
    return np.random.randint(0, 2, size=n, dtype=np.int8)

def noisy_channel(bits, error_prob=0.0):
    """Applica rumore casuale alla trasmissione dei bit"""
    if error_prob <= 0:
        return bits.copy()
    flips = np.random.rand(len(bits)) < error_prob
    return np.bitwise_xor(bits, flips.astype(np.int8))

# ---------------- INTERCETTAZIONE ----------------
def interception(alice_bits, alice_basis, n, eve_active=True):
    """
    Eve intercetta i bit solo se eve_active=True.
    Restituisce i bit misurati da Eve e le sue basi.
    """
    if not eve_active:
        return alice_bits.copy(), alice_basis.copy()  # nessuna intercettazione

    eve_basis = generate_basis(n)
    random_bits = np.random.randint(0, 2, size=n, dtype=np.int8)
    # Eve misura correttamente solo se la sua base coincide con quella di Alice
    eve_measures = np.where(eve_basis == alice_basis, alice_bits, random_bits)
    return eve_measures, eve_basis

# ---------------- RICEZIONE BOB ----------------
def bob_receive(sent_bits, sender_basis, n, error_prob=0.0):
    """
    Bob riceve i bit trasmessi.
    - sent_bits: bit inviati dal mittente (Alice o Eve)
    - sender_basis: basi usate dal mittente reale
    """
    bob_basis = generate_basis(n)
    random_bits = np.random.randint(0, 2, size=n, dtype=np.int8)
    # Bob misura correttamente solo se le basi coincidono
    bob_measure = np.where(bob_basis == sender_basis, sent_bits, random_bits)
    # applica rumore sul canale
    bob_measure = noisy_channel(bob_measure, error_prob)
    return bob_measure, bob_basis

# ---------------- SIFTING DELLA CHIAVE ----------------
def sift_key(alice_bits, alice_basis, bob_bits, bob_basis):
    """Mantiene solo i bit dove le basi coincidono"""
    mask = alice_basis == bob_basis
    alice_key = alice_bits[mask]
    bob_key = bob_bits[mask]
    discarded = np.sum(~mask)
    return alice_key, bob_key, discarded

# ---------------- CAMPIONE PER STIMA ERRORE ----------------
def sample_and_estimate_error(alice_key, bob_key, sample_size):
    n = len(alice_key)
    if n <= sample_size:
        sample_size = n // 2  # metà della chiave se molto piccola

    permutation = np.random.permutation(n)
    alice_perm = alice_key[permutation]
    bob_perm = bob_key[permutation]

    sample_indices = np.arange(sample_size)
    alice_sample = alice_perm[sample_indices]
    bob_sample = bob_perm[sample_indices]

    errors = np.sum(alice_sample != bob_sample)
    error_rate = errors / sample_size

    remaining_indices = np.arange(sample_size, n)
    alice_remaining = alice_perm[remaining_indices]
    bob_remaining = bob_perm[remaining_indices]

    return error_rate, alice_remaining, bob_remaining, alice_sample, bob_sample

# ---------------- MAIN ----------------
if __name__ == "__main__":
    n = 20000            # numero di bit iniziali
    sample_size = 8000     # campione per stima dell'errore
    eve_active = False    # True = Eve intercetta, False = nessuna intercettazione
    channel_error = 0.000 # probabilità di bit flip casuale sul canale

    # --- Alice genera bit e basi ---
    alice_bits = generate_bit(n)
    alice_basis = generate_basis(n)

    # --- Trasmissione: Eve intercetta (opzionale) ---
    transmitted_bits, sender_basis = interception(alice_bits, alice_basis, n, eve_active)

    # --- Bob riceve i bit ---
    bob_bits, bob_basis = bob_receive(transmitted_bits, sender_basis, n, error_prob=channel_error)

    # --- Sifting: mantieni solo bit dove basi coincidono ---
    alice_key, bob_key, discarded = sift_key(alice_bits, alice_basis, bob_bits, bob_basis)

    # --- Stima errore su un campione ---
    error_rate, alice_rem, bob_rem, alice_sample, bob_sample = sample_and_estimate_error(
        alice_key, bob_key, sample_size
    )

    # --- STAMPA RISULTATI ---
    '''print("Alice chiave siftata: ", alice_key)
    print("Bob chiave siftata:   ", bob_key)
    print("Campione Alice:       ", alice_sample)
    print("Campione Bob:         ", bob_sample)
    print("Chiave rimanente Alice:", alice_rem)
    print("Chiave rimanente Bob:  ", bob_rem)
    print("Bit scartati:", discarded)'''
    print("Errore stimato: {:.4f}".format(error_rate))
