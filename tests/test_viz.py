import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import visualize

def main():
    xs, ys = visualize.load_cities("cityData.txt")
    assert len(xs) == 42 and len(ys) == 42, "expected 42 cities"
    assert xs[0] == 170.0 and ys[0] == 85.0, "city 1 coords"

    tours, lengths = visualize.load_tours("results/tours.csv")
    assert len(tours) > 0, "no tours"
    assert len(tours[0]) == 42, "tour must have 42 cities"
    assert sorted(tours[0]) == list(range(1, 43)), "tour must be a permutation of 1..42"

    gens, best, avg = visualize.load_fitness("results/fitness.csv")
    assert len(gens) == len(best) == len(avg) and len(gens) > 0
    print("test_viz OK")

if __name__ == "__main__":
    main()
