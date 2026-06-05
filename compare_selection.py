"""Average the Roulette vs Tournament experiment and plot mean best-length curves.

Usage:
    python3 compare_selection.py
Writes results/selection_comparison.png and prints the mean final lengths.
"""
import csv
from collections import defaultdict
import matplotlib.pyplot as plt


def load_experiment(path="results/experiment.csv"):
    best = defaultdict(lambda: defaultdict(list))   # best[method][generation] = [lengths]
    avg = defaultdict(lambda: defaultdict(list))
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            m = row["method"]
            g = int(row["generation"])
            best[m][g].append(float(row["best_length"]))
            avg[m][g].append(float(row["avg_length"]))
    return best, avg


def mean_curve(per_generation):
    gens = sorted(per_generation.keys())
    means = [sum(per_generation[g]) / len(per_generation[g]) for g in gens]
    return gens, means


def main():
    best, avg = load_experiment()

    fig, ax = plt.subplots(figsize=(9, 6))
    colors = {"roulette": "tab:blue", "tournament": "tab:red"}
    print("Mean final best tour length (averaged over runs):")
    for method in sorted(best.keys()):
        gens, mean_best = mean_curve(best[method])
        ax.plot(gens, mean_best, label=f"{method} (mean best)", color=colors.get(method))
        print(f"  {method}: {mean_best[-1]:.1f}")

    ax.axhline(699, color="gray", ls="--", lw=1, label="optimal (699)")
    ax.set_title("Roulette vs Tournament — mean best tour length")
    ax.set_xlabel("generation"); ax.set_ylabel("mean best length")
    ax.legend()
    plt.tight_layout()
    plt.savefig("results/selection_comparison.png", dpi=120)
    print("Saved results/selection_comparison.png")


if __name__ == "__main__":
    main()
