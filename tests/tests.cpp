#include "GenericHeader.h"
#include "Utility.h"
#include "Sample.h"
#include "FitnessCalculator.h"
#include "Algorithm.h"
#include <cstdio>

static int g_failures = 0;
static int g_checks = 0;

#define CHECK(cond) do { ++g_checks; if(!(cond)) { ++g_failures; \
    printf("FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); } } while(0)

static bool isPermutation(const vector<int> &v, int n)
{
	if ((int)v.size() != n) return false;
	vector<char> seen(n, 0);
	for (int x : v) { if (x < 0 || x >= n || seen[x]) return false; seen[x] = 1; }
	return true;
}

static void test_rng_range()
{
	for (int i = 0; i < 200; i++)
	{
		int r = Utility::randomIndexGenerator(3, 7);
		CHECK(r >= 3 && r <= 7);
	}
}

static void test_rng_seed_reproducible()
{
	Utility::seed(42);
	int a1 = Utility::randomIndexGenerator(0, 1000000);
	Utility::seed(42);
	int a2 = Utility::randomIndexGenerator(0, 1000000);
	CHECK(a1 == a2);
}

static void test_distance_matrix_load()
{
	CHECK(Utility::loadDistanceMatrix("intercityDistance.txt"));
	CHECK((int)Utility::distanceMatrix.size() == 42);
	CHECK((int)Utility::distanceMatrix[0].size() == 42);
	CHECK(Utility::distanceMatrix[0][0] == 0);
	CHECK(Utility::distanceMatrix[0][1] == 8);
	CHECK(Utility::distanceMatrix[2][3] == 9);
	CHECK(Utility::distanceMatrix[2][3] == Utility::distanceMatrix[3][2]);
}

static void test_city_data_load()
{
	CHECK(Utility::loadCityData("cityData.txt"));
	CHECK((int)Utility::cityX.size() == 42);
	CHECK(Utility::cityX[0] == 170.0 && Utility::cityY[0] == 85.0);
	CHECK(Utility::cityX[41] == 174.0 && Utility::cityY[41] == 87.0);
}

static void test_random_tour_is_permutation()
{
	Utility::GENE_SIZE = 42;
	Utility::seed(5);
	Sample s;
	s.initRandomTour();
	vector<int> ids = s.tourAsCityIds();
	for (auto &x : ids) x -= 1;
	CHECK(isPermutation(ids, 42));
}

static void test_inversion_preserves_permutation()
{
	Utility::GENE_SIZE = 42;
	Utility::MUTATION_RATE = 1.0;
	Utility::MUTATION = Utility::INVERSION;
	Utility::seed(9);
	Sample s; s.initRandomTour();
	s.mutate();
	vector<int> ids = s.tourAsCityIds();
	for (auto &x : ids) x -= 1;
	CHECK(isPermutation(ids, 42));
}

static void test_swap_preserves_permutation()
{
	Utility::GENE_SIZE = 42;
	Utility::MUTATION_RATE = 1.0;
	Utility::MUTATION = Utility::SWAP;
	Utility::seed(11);
	Sample s; s.initRandomTour();
	s.mutate();
	vector<int> ids = s.tourAsCityIds();
	for (auto &x : ids) x -= 1;
	CHECK(isPermutation(ids, 42));
}

static Sample makeSampleFromOrder(const vector<int> &order)
{
	vector<GeneModel> g;
	for (int c : order) g.push_back(GeneModel(c));
	Sample s;
	s.setSample(g);
	return s;
}

static void test_tour_length_and_fitness()
{

	Utility::GENE_SIZE = 4;
	Utility::distanceMatrix = {
		{0, 1, 10, 10},
		{1, 0, 1, 10},
		{10, 1, 0, 1},
		{10, 10, 1, 0}
	};

	Sample good = makeSampleFromOrder({0, 1, 2, 3});
	Sample bad  = makeSampleFromOrder({0, 2, 1, 3});

	FitnessCalculator::calculateFitness(good);
	FitnessCalculator::calculateFitness(bad);

	CHECK(good.getTourLength() == 13.0);
	CHECK(bad.getTourLength() == 31.0);
	CHECK(good.getFitness() == 1.0 / 13.0);
	CHECK(good.getFitness() > bad.getFitness());
}

static void test_pmx_segment_and_validity()
{
	vector<int> p1 = {0,1,2,3,4,5,6,7,8};
	vector<int> p2 = {4,5,2,1,8,7,6,0,3};
	vector<int> child = Algorithm::pmxCore(p1, p2, 3, 6);
	CHECK(isPermutation(child, 9));
	CHECK(child[3]==3 && child[4]==4 && child[5]==5 && child[6]==6);
}

static void test_pmx_identical_parents()
{
	vector<int> p = {0,1,2,3,4};
	vector<int> child = Algorithm::pmxCore(p, p, 1, 3);
	CHECK(child == p);
}

static void test_pmx_random_validity()
{
	Utility::seed(7);
	for (int t = 0; t < 100; t++)
	{
		int n = 12;
		vector<int> a(n), b(n);
		for (int i = 0; i < n; i++) { a[i] = i; b[i] = i; }
		for (int i = n - 1; i > 0; i--) { int j = Utility::randomIndexGenerator(0, i); std::swap(b[i], b[j]); }
		int c1 = Utility::randomIndexGenerator(0, n - 1);
		int c2 = Utility::randomIndexGenerator(0, n - 1);
		CHECK(isPermutation(Algorithm::pmxCore(a, b, c1, c2), n));
	}
}

static void test_pmx_canonical_textbook_example()
{
	vector<int> p1 = {1,2,3,4,5,6,7,8,9};
	vector<int> p2 = {9,3,7,8,2,6,5,1,4};
	vector<int> child = Algorithm::pmxCore(p1, p2, 3, 6);
	vector<int> expected = {9,3,2,4,5,6,7,1,8};
	CHECK(child == expected);
}

static void test_ga_improves_on_dantzig()
{
	CHECK(Utility::loadDistanceMatrix("intercityDistance.txt"));
	Utility::seed(123);
	Utility::GENE_SIZE = 42;
	Utility::POPULATION_SIZE = 60;
	Utility::POPULATION_CROSSOVER_SIZE = 30;
	Utility::POPULATION_MAX_SIZE = 60;
	Utility::NUMBER_OF_ELITES = 2;
	Utility::MUTATION_RATE = 0.25;
	Utility::MUTATION = Utility::INVERSION;
	Utility::TOURNAMENT_SIZE = 5;
	Utility::CROSS_OVER = Utility::PMX;
	Utility::SAMPLE_SELECTION = Utility::TOURNAMENT_SELECTION;

	Population pop;
	for (int i = 0; i < Utility::POPULATION_SIZE; i++)
	{
		Sample s; s.initRandomTour();
		FitnessCalculator::calculateFitness(s);
		pop.addSample(s);
	}

	Algorithm::run(pop, 200);

	CHECK(!Algorithm::history.empty());
	double firstBest = Algorithm::history.front().bestLength;
	double lastBest  = Algorithm::history.back().bestLength;
	CHECK(lastBest <= firstBest);
	CHECK(lastBest < firstBest);

	vector<int> t = Algorithm::history.back().bestTour;
	for (auto &x : t) x -= 1;
	CHECK(isPermutation(t, 42));
}

static vector<double> runGaHistory(unsigned int seedValue)
{
	Utility::seed(seedValue);
	Population pop;
	for (int i = 0; i < Utility::POPULATION_SIZE; i++)
	{
		Sample s; s.initRandomTour();
		FitnessCalculator::calculateFitness(s);
		pop.addSample(s);
	}
	Algorithm::run(pop, 80);

	vector<double> bestPerGen;
	bestPerGen.reserve(Algorithm::history.size());
	for (const auto &g : Algorithm::history) bestPerGen.push_back(g.bestLength);
	return bestPerGen;
}

static void configureReproTestGA(Utility::SAMPLE_SELECTION_TYPE selection)
{
	CHECK(Utility::loadDistanceMatrix("intercityDistance.txt"));
	Utility::GENE_SIZE = 42;
	Utility::POPULATION_SIZE = 40;
	Utility::POPULATION_CROSSOVER_SIZE = 20;
	Utility::POPULATION_MAX_SIZE = 40;
	Utility::NUMBER_OF_ELITES = 2;
	Utility::MUTATION_RATE = 0.25;
	Utility::MUTATION = Utility::INVERSION;
	Utility::CROSS_OVER = Utility::PMX;
	Utility::TOURNAMENT_SIZE = 5;
	Utility::SAMPLE_SELECTION = selection;
}

static void test_roulette_reproducible()
{
	configureReproTestGA(Utility::ROULETTE_SELECTION);

	vector<double> a = runGaHistory(777);
	vector<double> b = runGaHistory(777);

	CHECK(a.back() == b.back());
	CHECK(a == b);
}

static void test_tournament_reproducible()
{
	configureReproTestGA(Utility::TOURNAMENT_SELECTION);

	vector<double> a = runGaHistory(777);
	vector<double> b = runGaHistory(777);

	CHECK(a.back() == b.back());
	CHECK(a == b);
}

int main()
{
	test_rng_range();
	test_rng_seed_reproducible();
	test_distance_matrix_load();
	test_city_data_load();

	test_random_tour_is_permutation();
	test_inversion_preserves_permutation();
	test_swap_preserves_permutation();

	test_tour_length_and_fitness();

	test_pmx_segment_and_validity();
	test_pmx_identical_parents();
	test_pmx_random_validity();
	test_pmx_canonical_textbook_example();

	test_ga_improves_on_dantzig();

	test_roulette_reproducible();
	test_tournament_reproducible();

	printf("\n%d checks, %d failures\n", g_checks, g_failures);
	return g_failures ? 1 : 0;
}
