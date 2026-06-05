"""Live animated dashboard for the TSP genetic algorithm.

Left panel:  the best tour of each generation drawn over the city map.
Right panel: best and average tour length over generations.

Usage:
    python3 visualize.py                 # live window
    python3 visualize.py --save tour.mp4 # render to a video file
"""
import csv
import sys
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def load_cities(path="cityData.txt"):
    xs, ys = [], []
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 3:
                continue
            xs.append(float(parts[1]))   # format: id x y
            ys.append(float(parts[2]))
    return xs, ys


def load_fitness(path="results/fitness.csv"):
    gens, best, avg = [], [], []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            gens.append(int(row["generation"]))
            best.append(float(row["best_length"]))
            avg.append(float(row["avg_length"]))
    return gens, best, avg


def load_tours(path="results/tours.csv"):
    tours, lengths = [], []
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            lengths.append(float(row[1]))
            tours.append([int(x) for x in row[2:]])
    return tours, lengths


def main():
    save_path = None
    if "--save" in sys.argv:
        i = sys.argv.index("--save") + 1
        if i >= len(sys.argv):
            print("Usage: python3 visualize.py [--save <file>]")
            return
        save_path = sys.argv[i]

    xs, ys = load_cities()
    gens, best, avg = load_fitness()
    tours, lengths = load_tours()

    # subsample so very long runs animate smoothly (~300 frames max),
    # always including the final generation (the converged best tour)
    step = max(1, len(tours) // 300)
    frames = list(range(0, len(tours), step))
    if frames and frames[-1] != len(tours) - 1:
        frames.append(len(tours) - 1)

    fig, (ax_map, ax_fit) = plt.subplots(1, 2, figsize=(13, 6))

    ax_map.scatter(xs, ys, c="crimson", s=30, zorder=3)
    (tour_line,) = ax_map.plot([], [], "-", c="steelblue", lw=1.5, zorder=2)
    ax_map.set_xlabel("x"); ax_map.set_ylabel("y")

    ax_fit.set_title("Tour length over generations")
    ax_fit.set_xlabel("generation"); ax_fit.set_ylabel("tour length")
    (best_line,) = ax_fit.plot([], [], c="green", label="best")
    (avg_line,) = ax_fit.plot([], [], c="orange", label="average")
    ax_fit.axhline(699, color="gray", ls="--", lw=1, label="optimal (699)")
    ax_fit.legend()
    ax_fit.set_xlim(0, max(gens) if gens else 1)
    if best and avg:
        ax_fit.set_ylim(min(best) * 0.95, max(avg) * 1.05)

    def coords_for(tour):
        px = [xs[c - 1] for c in tour] + [xs[tour[0] - 1]]
        py = [ys[c - 1] for c in tour] + [ys[tour[0] - 1]]
        return px, py

    def update(frame):
        tour = tours[frame]
        px, py = coords_for(tour)
        tour_line.set_data(px, py)
        ax_map.set_title(f"Best tour — gen {gens[frame]} — length {lengths[frame]:.0f}")
        best_line.set_data(gens[:frame + 1], best[:frame + 1])
        avg_line.set_data(gens[:frame + 1], avg[:frame + 1])
        return tour_line, best_line, avg_line

    anim = FuncAnimation(fig, update, frames=frames, interval=50, blit=False, repeat=False)

    if save_path:
        anim.save(save_path, fps=20)
        print(f"Saved animation to {save_path}")
    else:
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()
