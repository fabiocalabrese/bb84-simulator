import random

def simulate_bb84(n_bits):
    alice_bits = []
    alice_bases = []
    bob_bases = []
    bob_results = []
    sifted_key = []

    for _ in range(n_bits):
        # Alice genera un bit e una base
        bit = 0 if random.random() < 0.5 else 1
        base_alice = '+' if random.random() < 0.5 else 'x'

        # Bob sceglie una base
        base_bob = '+' if random.random() < 0.5 else 'x'

        # Misura di Bob
        if base_bob == base_alice:
            # Bob ottiene il bit corretto
            result = bit
        else:
            # Bob ottiene un bit casuale
            result = 0 if bit == 0 else 1

        # Salvataggio
        alice_bits.append(bit)
        alice_bases.append(base_alice)
        bob_bases.append(base_bob)
        bob_results.append(result)

        # Sifting: si tiene solo se le basi coincidono
        if base_bob == base_alice:
            sifted_key.append(bit)
        else:
            sifted_key.append(None)  # solo per visualizzare i mismatch

    return alice_bits, alice_bases, bob_bases, bob_results, sifted_key


# --- test ---
N = 256
alice_bits, alice_bases, bob_bases, bob_results, sifted = simulate_bb84(N)

print("Alice bits:   ", alice_bits)
print("Alice bases:  ", alice_bases)
print("Bob bases:    ", bob_bases)
print("Bob results:  ", bob_results)
print("Sifted key:   ", sifted)
print("Chiave finale:", [b for b in sifted if b is not None])
