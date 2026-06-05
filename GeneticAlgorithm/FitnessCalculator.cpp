#include "FitnessCalculator.h"
#include "Utility.h"

FitnessCalculator::FitnessCalculator(void) {}

double FitnessCalculator::tourLengthOf(const Sample &sample)
{
	const vector<vector<int>> &dist = Utility::distanceMatrix;
	int n = (int)sample.gene.size();
	double total = 0.0;
	for (int i = 0; i < n; i++)
	{
		int from = sample.gene[i].data;
		int to = sample.gene[(i + 1) % n].data;
		total += dist[from][to];
	}
	return total;
}

void FitnessCalculator::calculateFitness(Sample &sample)
{
	double length = tourLengthOf(sample);
	sample.tourLength = length;

	sample.fitness = (length > 0.0) ? (1.0 / length) : 0.0;
}

FitnessCalculator::~FitnessCalculator(void) {}
