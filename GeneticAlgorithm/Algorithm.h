#ifndef ALGORITHM_H_
#define ALGORITHM_H_

#include "Population.h"
#include "Sample.h"
#include "FitnessCalculator.h"
#include "GeneModel.h"

class Algorithm
{
public:
	struct GenerationStat
	{
		int generation;
		double bestLength;
		double avgLength;
		vector<int> bestTour;
	};
	static vector<GenerationStat> history;

	static void recordGeneration(Population &, int generation);

	static void checkParameters();
	static void run(Population &, int);
	static void evolvePopulation(Population &);
	static void evaluateFitnesses(Population &);
	static void performSelection(Population &);
	static void crossOver(Population &);
	static void mutate(Population &);

	static void crossOverOnePoint(Population &, Sample, Sample);
	static void crossOverTwoPoint(Population &, Sample, Sample);
	static void crossOverUniform(Population &, Sample, Sample);
	static void crossOverWholeArithmeticRecombination(Population &, Sample, Sample);

	static vector<int> pmxCore(const vector<int> &p1, const vector<int> &p2, int cut1, int cut2);
	static void crossOverPMX(Population &, Sample, Sample);

	static void performRoulletteSelection(Population &);
	static void performTournamentSelection(Population &);
	static void normalizeFitnesses(Population &);

private:
	static vector<Sample> matingPool;

	static void printMatingPool();

    static double alpha;

	Algorithm(void);
	~Algorithm(void);
};

#endif
