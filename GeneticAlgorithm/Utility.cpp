#include "Utility.h"

int Utility::GENE_SIZE = 0;

int Utility::POPULATION_SIZE = 0;
int Utility::POPULATION_CROSSOVER_SIZE = 10;
int Utility::POPULATION_MAX_SIZE = 100;
int Utility::ID_COUNTER = 0;

double Utility::MUTATION_RATE = 0.030;
int Utility::CUT_LENGTH = 2;
int Utility::NUMBER_OF_ELITES = 2;
double Utility::PERCENT_IMPROVEMENT = 10.0;

int Utility::TOURNAMENT_SIZE = 10;
int Utility::NUMBER_OF_TOURNAMENTS = 8;

Utility::CROSS_OVER_TYPE Utility::CROSS_OVER = Utility::PMX;
Utility::SAMPLE_SELECTION_TYPE Utility::SAMPLE_SELECTION = Utility::TOURNAMENT_SELECTION;
Utility::MUTATION_TYPE Utility::MUTATION = Utility::INVERSION;

vector<vector<int>> Utility::distanceMatrix;
vector<double> Utility::cityX;
vector<double> Utility::cityY;

static std::mt19937 &engine()
{
	static std::mt19937 gen(123456789u);
	return gen;
}

void Utility::seed(unsigned int seedValue)
{
	engine().seed(seedValue);
}

int Utility::randomIndexGenerator(int min, int max)
{
	std::uniform_int_distribution<int> uni(min, max);
	return uni(engine());
}

double Utility::randomValueGenerator()
{
	std::uniform_real_distribution<double> uni(0.0, 1.0);
	return uni(engine());
}

bool Utility::loadDistanceMatrix(const string &path)
{
	std::ifstream in(path);
	if (!in) { cout << "Error: cannot open " << path << endl; return false; }

	distanceMatrix.clear();
	string line;

	while (std::getline(in, line))
	{
		std::istringstream ss(line);
		vector<int> row;
		int value;
		while (ss >> value) row.push_back(value);
		if (!row.empty()) distanceMatrix.push_back(row);
	}
	return !distanceMatrix.empty();
}

bool Utility::loadCityData(const string &path)
{
	std::ifstream in(path);
	if (!in) { cout << "Error: cannot open " << path << endl; return false; }

	cityX.clear();
	cityY.clear();
	string line;

	while (std::getline(in, line))
	{
		std::istringstream ss(line);
		int id; double x, y;
		if (!(ss >> id >> x >> y)) continue;
		cityX.push_back(x);
		cityY.push_back(y);
	}
	return !cityX.empty();
}

Utility::Utility(void) {}
Utility::~Utility(void) {}
