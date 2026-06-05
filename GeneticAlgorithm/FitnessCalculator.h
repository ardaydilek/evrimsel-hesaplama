#ifndef FITNESS_CALCULATOR_H_
#define FITNESS_CALCULATOR_H_

#include "Sample.h"

class FitnessCalculator
{
public:
	FitnessCalculator(void);

	static double tourLengthOf(const Sample &sample);

	static void calculateFitness(Sample &sample);

	~FitnessCalculator(void);
};

#endif
