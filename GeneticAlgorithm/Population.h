#ifndef POPULATION_H_
#define POPULATION_H_

#include "GenericHeader.h"
#include "Sample.h"
#include "Utility.h"

class Population
{
public:
	friend class Algorithm;

	Population(void);
	~Population(void);

	Sample getFittest();
	void addSample(Sample &);
	void sort();

	void cleanUp();
	void printSampleFitnesses();
	void printSampleDetail();

private:
	vector<Sample> sampleList;
};

#endif
