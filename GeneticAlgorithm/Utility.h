#ifndef UTILITY_H_
#define UTILITY_H_

#include "GenericHeader.h"

class Utility
{
public:
	static int GENE_SIZE;

	static int POPULATION_SIZE;
	static int POPULATION_CROSSOVER_SIZE;
	static int POPULATION_MAX_SIZE;
	static int ID_COUNTER;

	static double MUTATION_RATE;
	static int CUT_LENGTH;
	static int NUMBER_OF_ELITES;
	static double PERCENT_IMPROVEMENT;

	static int TOURNAMENT_SIZE;
	static int NUMBER_OF_TOURNAMENTS;

	enum CROSS_OVER_TYPE{ONE_POINT, TWO_POINT, UNIFORM, PMX};
	enum SAMPLE_SELECTION_TYPE{ROULETTE_SELECTION, TOURNAMENT_SELECTION};
	enum MUTATION_TYPE{INVERSION, SWAP};

	static CROSS_OVER_TYPE CROSS_OVER;
	static SAMPLE_SELECTION_TYPE SAMPLE_SELECTION;
	static MUTATION_TYPE MUTATION;

	static void seed(unsigned int seedValue);
	static int randomIndexGenerator(int min, int max);
	static double randomValueGenerator();

	static bool loadDistanceMatrix(const string &path);
	static bool loadCityData(const string &path);

	static vector<vector<int>> distanceMatrix;
	static vector<double> cityX;
	static vector<double> cityY;

	Utility(void);
	~Utility(void);
};

#endif
