import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import compare_selection

def main():
    best, avg = compare_selection.load_experiment("results/experiment.csv")
    assert set(best.keys()) == {"roulette", "tournament"}, best.keys()
    g, mean = compare_selection.mean_curve(best["tournament"])
    assert len(g) == len(mean) and len(g) > 0
    print("test_compare OK")

if __name__ == "__main__":
    main()
