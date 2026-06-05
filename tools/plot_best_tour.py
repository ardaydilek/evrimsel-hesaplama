"""En iyi GA turunu 42 Dantzig şehrinin koordinatları üzerine çizer -> assets/best_tour.png.
cityData.txt (id x y) ve results/best_tour.txt (3. satır = 1-tabanlı ziyaret sırası) okunur."""
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load_coords(path="cityData.txt"):
    coords = {}
    for line in pathlib.Path(path).read_text().splitlines():
        parts = line.split()
        if len(parts) >= 3:
            coords[int(parts[0])] = (float(parts[1]), float(parts[2]))
    return coords


def load_tour(path="results/best_tour.txt"):
    lines = pathlib.Path(path).read_text().splitlines()
    length = int(lines[0].split(":")[1])
    order = [int(t) for t in lines[2].split()]
    return length, order


def main():
    coords = load_coords()
    length, order = load_tour()
    xs = [coords[c][0] for c in order] + [coords[order[0]][0]]
    ys = [coords[c][1] for c in order] + [coords[order[0]][1]]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(xs, ys, "-", color="#0d9488", linewidth=1.6, zorder=1)
    ax.scatter([coords[c][0] for c in coords], [coords[c][1] for c in coords],
               color="#111827", s=28, zorder=2)
    for cid, (x, y) in coords.items():
        ax.annotate(str(cid), (x, y), textcoords="offset points", xytext=(3, 3), fontsize=7)
    ax.set_title(f"Dantzig42 — en iyi tur (uzunluk = {length}, optimum = 699)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal", adjustable="datalim")
    fig.tight_layout()
    pathlib.Path("assets").mkdir(exist_ok=True)
    fig.savefig("assets/best_tour.png", dpi=150)
    print("wrote assets/best_tour.png  (length", length, ")")


if __name__ == "__main__":
    main()
