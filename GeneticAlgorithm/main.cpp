#include "GenericHeader.h"
#include "Algorithm.h"
#include "FitnessCalculator.h"
#include <filesystem>

static const int GENERATIONS = 2500;

static void configureGA()
{
	Utility::GENE_SIZE = 42;
	Utility::POPULATION_SIZE = 320;
	Utility::POPULATION_CROSSOVER_SIZE = 160;
	Utility::POPULATION_MAX_SIZE = 320;
	Utility::NUMBER_OF_ELITES = 2;
	Utility::MUTATION_RATE = 0.35;
	Utility::MUTATION = Utility::INVERSION;
	Utility::TOURNAMENT_SIZE = 4;
	Utility::CROSS_OVER = Utility::PMX;
	Utility::SAMPLE_SELECTION = Utility::TOURNAMENT_SELECTION;
}

static Population buildInitialPopulation()
{
	Population population;
	for (int i = 0; i < Utility::POPULATION_SIZE; i++)
	{
		Sample s;
		s.initRandomTour();
		FitnessCalculator::calculateFitness(s);
		population.addSample(s);
	}
	return population;
}

static void writeFitnessCsv(const string &path)
{
	std::ofstream out(path);
	out << "generation,best_length,avg_length\n";
	for (const auto &s : Algorithm::history)
		out << s.generation << "," << s.bestLength << "," << s.avgLength << "\n";
}

static void writeToursCsv(const string &path)
{
	std::ofstream out(path);
	out << "generation,length";
	for (int i = 0; i < Utility::GENE_SIZE; i++) out << ",c" << (i + 1);
	out << "\n";
	for (const auto &s : Algorithm::history)
	{
		out << s.generation << "," << s.bestLength;
		for (int id : s.bestTour) out << "," << id;
		out << "\n";
	}
}

static void writeBestTourTxt(const string &path)
{
	const Algorithm::GenerationStat &last = Algorithm::history.back();
	std::ofstream out(path);
	out << "Best tour length: " << last.bestLength << "\n";
	out << "City visiting order (1-based):\n";
	for (int id : last.bestTour) out << id << " ";
	out << "\n";
}

static void runSolve()
{
	Utility::seed(42);
	Population population = buildInitialPopulation();
	Algorithm::run(population, GENERATIONS);

	writeFitnessCsv("results/fitness.csv");
	writeToursCsv("results/tours.csv");
	writeBestTourTxt("results/best_tour.txt");

	const Algorithm::GenerationStat &last = Algorithm::history.back();
	printf("\n=== solve complete ===\n");
	printf("Best tour length: %.1f (optimal = 699)\n", last.bestLength);
	printf("City order: ");
	for (int id : last.bestTour) printf("%d ", id);
	printf("\nResults written to results/\n");
}

static void runExperiment()
{
	const int RUNS = 10;
	const int EXP_GENERATIONS = 800;

	std::ofstream out("results/experiment.csv");
	out << "method,run,generation,best_length,avg_length\n";

	struct Method { const char *name; Utility::SAMPLE_SELECTION_TYPE sel; };
	Method methods[2] = {
		{ "roulette",   Utility::ROULETTE_SELECTION },
		{ "tournament", Utility::TOURNAMENT_SELECTION }
	};

	for (int m = 0; m < 2; m++)
	{
		Utility::SAMPLE_SELECTION = methods[m].sel;
		for (int run = 0; run < RUNS; run++)
		{
			Utility::seed(1000 + run);
			Population population = buildInitialPopulation();
			Algorithm::run(population, EXP_GENERATIONS);

			for (const auto &s : Algorithm::history)
				out << methods[m].name << "," << run << "," << s.generation
				    << "," << s.bestLength << "," << s.avgLength << "\n";

			printf("[%s] run %d: best = %.1f\n",
			       methods[m].name, run, Algorithm::history.back().bestLength);
		}
	}
	printf("Experiment results written to results/experiment.csv\n");
}

int main(int argc, char **argv)
{
	string mode = (argc > 1) ? argv[1] : "solve";

	if (!Utility::loadDistanceMatrix("intercityDistance.txt") ||
	    !Utility::loadCityData("cityData.txt"))
	{
		cout << "Failed to load data files. Run ./tsp from the project root." << endl;
		return 1;
	}

	std::filesystem::create_directories("results");
	configureGA();

	if (mode == "solve")
	{
		runSolve();
	}
	else if (mode == "experiment")
	{
		runExperiment();
	}
	else
	{
		cout << "Usage: ./tsp [solve|experiment]" << endl;
		return 1;
	}

	return 0;
}
