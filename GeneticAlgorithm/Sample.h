#ifndef SAMPLE_H_
#define SAMPLE_H_

#include "GenericHeader.h"
#include "GeneModel.h"
#include "Utility.h"

class Sample
{
	friend class Population;
	friend class Algorithm;
	friend class FitnessCalculator;

public:
	Sample(void);
	Sample(const Sample &sample);

	void setSample(vector<GeneModel> sample);
	void initRandomTour();

	double getFitness();
	double getNormalizedFitness();
	double getTourLength();

	void setFitness(double fitness);
	void setNormalizedFitness(double normalizedFitness);

	void mutate();

	vector<int> tourAsCityIds() const;

	void printSample();

	~Sample(void);
private:
	int sampleID;
	double fitness;
	double normalizedFitness;
	double accumulatedFitness;
	double tourLength;

	vector<GeneModel> gene;
};

#endif
