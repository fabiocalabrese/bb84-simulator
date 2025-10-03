import numpy as np
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import csv


def bb84_banner():
    print("\n=== BB84 Quantum Key Distribution Simulator ===")
    print("By Fabio Calabrese (fabiocalabrese88@gmail.com)\n")


# ---------------- BB84 FUNCTIONS ----------------
def generate_bit(n):
    return np.random.randint(0, 2, size=n, dtype=np.int8)


def generate_basis(n):
    return np.random.randint(0, 2, size=n, dtype=np.int8)


def noisy_channel(bits, error_prob=0.0):
    flips = np.random.rand(len(bits)) < error_prob
    return np.bitwise_xor(bits, flips.astype(np.int8))


def interception_partial(alice_bits, alice_basis, n, eve_active=True, p_eve=1.0):
    """
    Intercept only a fraction of bits (intercept-resend).
    - p_eve: fraction intercepted (0.0..1.0)
    Returns: (transmitted_bits, sender_basis)
    """
    if not eve_active or p_eve <= 0:
        return alice_bits.copy(), alice_basis.copy()

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
    Binary search to locate error in a block.
    Returns corrected bob_block.
    """
    n = len(alice_block)
    if n == 0:
        return bob_block

    if np.bitwise_xor.reduce(alice_block) == np.bitwise_xor.reduce(bob_block):
        return bob_block

    if n == 1:
        bob_block[0] ^= 1
        return bob_block

    mid = n // 2
    alice_left, bob_left = alice_block[:mid], bob_block[:mid]
    alice_right, bob_right = alice_block[mid:], bob_block[mid:]

    if np.bitwise_xor.reduce(alice_left) != np.bitwise_xor.reduce(bob_left):
        corrected_left = binary_search_error(alice_left, bob_left)
        return np.concatenate((corrected_left, bob_right))
    else:
        corrected_right = binary_search_error(alice_right, bob_right)
        return np.concatenate((bob_left, corrected_right))


def block_error_correction(alice_key, bob_key, num_blocks=4):
    """
    Divide key into num_blocks and apply binary search
    to correct blocks with mismatched parity.
    Returns corrected Bob key.
    """
    n = len(alice_key)
    corrected_bob = bob_key.copy()
    block_size = max(1, n // num_blocks)

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        alice_block = alice_key[start:end]
        bob_block = corrected_bob[start:end]

        if np.bitwise_xor.reduce(alice_block) != np.bitwise_xor.reduce(bob_block):
            corrected_block = binary_search_error(alice_block, bob_block)
            corrected_bob[start:end] = corrected_block

    return corrected_bob


# ---------------- SIMULATION FUNCTION ----------------
def simulate_bb84(n, sample_size, eve_active=False, channel_error=0.0, p_eve=1.0):
    alice_bits = generate_bit(n)
    alice_basis = generate_basis(n)

    transmitted_bits, sender_basis = interception_partial(alice_bits, alice_basis, n,
                                                          eve_active=eve_active, p_eve=p_eve)
    bob_bits, bob_basis = bob_receive(transmitted_bits, sender_basis, n, error_prob=channel_error)

    alice_key, bob_key = sift_key(alice_bits, alice_basis, bob_bits, bob_basis)
    error_rate = sample_and_estimate_error(alice_key, bob_key, sample_size)
    key_length = len(alice_key)

    corrected_bob_key = block_error_correction(alice_key, bob_key, num_blocks=50)
    if len(alice_key) > 0:
        residual_error = np.mean(alice_key != corrected_bob_key)
    else:
        residual_error = 0

    return error_rate, key_length, residual_error


# ---------------- MULTIPLE SIMULATION ----------------
bb84_banner()

try:
    n = int(input("Enter number of bits per run (e.g., 100): "))
    sample_size = int(input("Enter sample size for error estimation (e.g., 2048): "))
    runs = int(input("Enter number of runs per channel_error (e.g., 500): "))
    channel_errors_input = input("Enter channel_error values separated by comma (e.g., 0,0.01,0.05): ")
    channel_errors = [float(x.strip()) for x in channel_errors_input.split(",")]
    p_eve = float(input("Enter Eve's interception fraction (e.g., 1.0 = 100%, 0.5 = 50%): "))
except ValueError:
    print("Invalid input, using default parameters.")
    n = 2048
    sample_size = 1024
    runs = 500
    channel_errors = [round(x * 0.01, 2) for x in range(0, 21)]  # 0 to 0.2 step 0.01
    p_eve = 0.2

print(f"\nSimulation ready with the following parameters:")
print(f"- Number of bits: {n}")
print(f"- Sample size: {sample_size}")
print(f"- Number of runs: {runs}")
print(f"- Channel errors: {channel_errors}")
print(f"- Eve interception fraction: {p_eve}")

# Results (errors and lengths)
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

# ---------------- PLOT 1: QBER ----------------
plt.figure(figsize=(8, 5))

# Estimated QBER (before correction)
mean_off = np.array(error_mean_eve_off)
std_off = np.array(error_std_eve_off)
plt.plot(channel_errors, mean_off, marker='o', label="QBER Eve off (before correction)")
plt.fill_between(channel_errors, mean_off - std_off, mean_off + std_off, color='skyblue', alpha=0.3)

mean_on = np.array(error_mean_eve_on)
std_on = np.array(error_std_eve_on)
plt.plot(channel_errors, mean_on, marker='o', label="QBER Eve on (before correction)")
plt.fill_between(channel_errors, mean_on - std_on, mean_on + std_on, color='salmon', alpha=0.3)

# Residual error (after correction)
mean_res_off = np.array(residual_mean_eve_off)
std_res_off = np.array(residual_std_eve_off)
plt.plot(channel_errors, mean_res_off, marker='s', linestyle='--', color='red',
         label="Residual Eve off (after correction)")
plt.fill_between(channel_errors, mean_res_off - std_res_off, mean_res_off + std_res_off, color='red', alpha=0.3)

mean_res_on = np.array(residual_mean_eve_on)
std_res_on = np.array(residual_std_eve_on)
plt.plot(channel_errors, mean_res_on, marker='s', linestyle='--', color='green',
         label="Residual Eve on (after correction)")
plt.fill_between(channel_errors, mean_res_on - std_res_on, mean_res_on + std_res_on, color='green', alpha=0.3)

# Reference lines
plt.plot(channel_errors, channel_errors, 'k--', label="Theoretical QBER (noise)")
plt.axhline(0.25 * p_eve, color='gray', linestyle=':', label=f"Theoretical QBER Eve ({p_eve * 100:.0f}%)")

plt.xlabel("Channel error probability")
plt.ylabel("Error (QBER or residual)")
plt.title("QBER before and after correction in BB84")
plt.grid(True)
plt.legend()
plt.show()

# ---------------- PLOT 2: KEY LENGTH ----------------
plt.figure(figsize=(8, 5))

mean_len_off = np.array(length_mean_eve_off)
std_len_off = np.array(length_std_eve_off)
plt.plot(channel_errors, mean_len_off, marker='o', label="Eve off")
plt.fill_between(channel_errors, mean_len_off - std_len_off, mean_len_off + std_len_off, color='skyblue', alpha=0.3)

mean_len_on = np.array(length_mean_eve_on)
std_len_on = np.array(length_std_eve_on)
plt.plot(channel_errors, mean_len_on, marker='o', label="Eve on")
plt.fill_between(channel_errors, mean_len_on - std_len_on, mean_len_on + std_len_on, color='salmon', alpha=0.3)

plt.xlabel("Channel error probability")
plt.ylabel("Average sifted key length")
plt.title("Sifted key length vs channel noise")
plt.grid(True)
plt.legend()
plt.show()

# ---------------- FINAL HISTOGRAMS ----------------
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.hist(errors_off_final, bins=30, color='skyblue', edgecolor='black')
plt.title("Error distribution Eve off (max c.e)")
plt.xlabel("Estimated error")
plt.ylabel("Frequency")

plt.subplot(1, 2, 2)
plt.hist(errors_on_final, bins=30, color='salmon', edgecolor='black')
plt.title("Error distribution Eve on (max c.e)")
plt.xlabel("Estimated error")
plt.ylabel("Frequency")

plt.tight_layout()
plt.show()

# ---------------- SAVE RESULTS ----------------
with open("bb84_results.csv", mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["channel_error",
                     "mean_QBER_eve_off", "std_QBER_eve_off",
                     "mean_QBER_eve_on", "std_QBER_eve_on",
                     "mean_len_eve_off", "std_len_eve_off",
                     "mean_len_eve_on", "std_len_eve_on",
                     "mean_residual_eve_off", "std_residual_eve_off",
                     "mean_residual_eve_on", "std_residual_eve_on"])

    for i, ce in enumerate(channel_errors):
        writer.writerow([ce,
                         error_mean_eve_off[i], error_std_eve_off[i],
                         error_mean_eve_on[i], error_std_eve_on[i],
                         length_mean_eve_off[i], length_std_eve_off[i],
                         length_mean_eve_on[i], length_std_eve_on[i],
                         residual_mean_eve_off[i], residual_std_eve_off[i],
                         residual_mean_eve_on[i], residual_std_eve_on[i]])

print("\nResults saved to 'bb84_results.csv'.")
