#include "Algorithm.h"
#include "Utility.h"

vector<Sample> Algorithm::matingPool;

vector<Algorithm::GenerationStat> Algorithm::history;

double Algorithm::alpha = 0.6;

Algorithm::Algorithm(void)
{

}

void Algorithm::checkParameters()
{
	if(Utility::NUMBER_OF_ELITES > Utility::POPULATION_SIZE)
	{
		printf("NUMBER_OF_ELITES (%d) cannot be greater than POPULATION_SIZE (%d).\n", Utility::NUMBER_OF_ELITES, Utility::POPULATION_SIZE);
		exit(-1);
	}

	if(Utility::GENE_SIZE <= 0)
	{
		printf("GENE_SIZE (%d) must be greater than 0.\n", Utility::GENE_SIZE);
		exit(-1);
	}

	if(Utility::POPULATION_SIZE <= 0)
	{
		printf("POPULATION_SIZE (%d) must be greater than 0.\n", Utility::POPULATION_SIZE);
		exit(-1);
	}

	if(Utility::CUT_LENGTH > Utility::GENE_SIZE)
	{
		printf("CUT_LENGTH (%d) cannot be greater than GENE_SIZE (%d).\n", Utility::CUT_LENGTH, Utility::GENE_SIZE);
		exit(-1);
	}
}

void Algorithm::run(Population & population, int numberOfGenerations)
{
	checkParameters();
	history.clear();

	for(int generation=0; generation<numberOfGenerations; generation++)
	{
		evolvePopulation(population);
		recordGeneration(population, generation);

		if (generation % 100 == 0)
			printf("Generation %d: best length = %.1f\n", generation, population.getFittest().getTourLength());
	}
}

void Algorithm::recordGeneration(Population & population, int generation)
{
	double sum = 0.0;
	int count = (int)population.sampleList.size();
	for (int i = 0; i < count; i++)
		sum += population.sampleList[i].tourLength;

	Sample best = population.getFittest();

	GenerationStat stat;
	stat.generation = generation;
	stat.bestLength = best.tourLength;
	stat.avgLength = (count > 0) ? sum / count : 0.0;
	stat.bestTour = best.tourAsCityIds();
	history.push_back(stat);
}

void Algorithm::evolvePopulation(Population & population)
{

	evaluateFitnesses(population);

	crossOver(population);

	mutate(population);

	evaluateFitnesses(population);

	population.sort();

	population.cleanUp();
}

void Algorithm::evaluateFitnesses(Population & population)
{
	for(int sampleIndex=0; sampleIndex<population.sampleList.size(); sampleIndex++)
	{
		FitnessCalculator::calculateFitness(population.sampleList[sampleIndex]);
	}

	normalizeFitnesses(population);
}

void Algorithm::crossOver(Population & population)
{

	performSelection(population);

	if(matingPool.size() == 0)
	{
        printf("No individuals could be selected! Skipping recombination\n");
        return;
	}

	for(int recombNumber=0; recombNumber<Utility::POPULATION_CROSSOVER_SIZE; recombNumber++)
	{
		int parent1Index = Utility::randomIndexGenerator(0, matingPool.size()-1);
		int parent2Index = Utility::randomIndexGenerator(0, matingPool.size()-1);

		Sample parent1 = matingPool[parent1Index];
		Sample parent2 = matingPool[parent2Index];

		switch(Utility::CROSS_OVER)
		{
			case  Utility::ONE_POINT:
				crossOverOnePoint(population, parent1, parent2);
			break;

			case  Utility::TWO_POINT:
				crossOverTwoPoint(population, parent1, parent2);
			break;

			case  Utility::UNIFORM:
				crossOverUniform(population, parent1, parent2);
			break;

			case  Utility::PMX:
				crossOverPMX(population, parent1, parent2);
			break;
		}
	}

}

void Algorithm::mutate(Population & population)
{
	vector<Sample>::iterator it;

	for(it = population.sampleList.begin() + Utility::NUMBER_OF_ELITES; it !=  population.sampleList.end(); ++it)
	{
		it->mutate();
	}
}

void Algorithm::normalizeFitnesses(Population & population)
{
	double fitnessSum = 0.0;
	vector<Sample>::iterator it;
	for(it = population.sampleList.begin(); it != population.sampleList.end(); ++it)
	{
		fitnessSum += it->fitness;
	}

	for(it = population.sampleList.begin(); it != population.sampleList.end(); ++it)
	{
		it->normalizedFitness = it->fitness / fitnessSum;
	}
}

void Algorithm::performSelection(Population & population)
{
	switch(Utility::SAMPLE_SELECTION)
	{
		case Utility::ROULETTE_SELECTION:
			performRoulletteSelection(population);
		break;

		case Utility::TOURNAMENT_SELECTION:
			performTournamentSelection(population);
		break;
	}
}

void Algorithm::performRoulletteSelection(Population & population)
{

	matingPool.clear();

	normalizeFitnesses(population);

	vector<Sample>::iterator it1;
	for(it1 = population.sampleList.begin(); it1 != population.sampleList.end(); ++it1)
	{
		double fitnessAcc = 0.0;
		vector<Sample>::iterator it2;
		for(it2 = population.sampleList.begin(); it2 != it1+1; ++it2)
		{
			fitnessAcc += it2->normalizedFitness;
		}

		it1->accumulatedFitness = fitnessAcc;
	}

	for(int sampleNumber=0; sampleNumber < Utility::POPULATION_CROSSOVER_SIZE; sampleNumber++)
	{

		double random = Utility::randomValueGenerator();

		vector<Sample>::iterator it;
		for(it = population.sampleList.begin(); it != population.sampleList.end(); ++it)
		{
			if(it->accumulatedFitness > random)
			{
				matingPool.push_back(*it);
				break;
			}
		}
	}
}

void Algorithm::performTournamentSelection(Population & population)
{

	matingPool.clear();

	Utility::NUMBER_OF_TOURNAMENTS = Utility::POPULATION_CROSSOVER_SIZE;

	vector<vector<Sample>> tournaments;
	tournaments.reserve(Utility::NUMBER_OF_TOURNAMENTS);

	for(int i=0; i<Utility::NUMBER_OF_TOURNAMENTS;i++)
	{
		vector<Sample> tournament;

		tournaments.push_back(tournament);

		tournaments[i].reserve(Utility::TOURNAMENT_SIZE);

		for(int count=0; count<Utility::TOURNAMENT_SIZE; count++)
		{
			int randomIndex = Utility::randomIndexGenerator(0, population.sampleList.size()-1);
			tournaments[i].push_back(population.sampleList[randomIndex]);
		}
	}

	matingPool.reserve(Utility::NUMBER_OF_TOURNAMENTS);

	for(int i=0; i<Utility::NUMBER_OF_TOURNAMENTS; i++)
	{
		int fittestIndex = -1;
		double bestFitness = 0.0;
		for(int j=0; j<Utility::TOURNAMENT_SIZE; j++)
		{
			if((tournaments[i])[j].fitness >= bestFitness)
			{
				fittestIndex = j;
				bestFitness = (tournaments[i])[j].fitness;
			}
		}

		matingPool.push_back((tournaments[i])[fittestIndex]);
	}
}

void Algorithm::printMatingPool()
{
	int size = matingPool.size();

	for(int i=0; i<size; i++)
	{
		matingPool[i].printSample();
	}
}

void Algorithm::crossOverOnePoint(Population & population, Sample parent1, Sample parent2)
{

	Sample child1 = Sample(parent1);
	Sample child2 = Sample(parent2);

	int cutIndex = (int)(Utility::GENE_SIZE / 2);

	for(int index = cutIndex; index < Utility::GENE_SIZE; index++)
	{
		child1.gene[index] = parent2.gene[index];
		child2.gene[index] = parent1.gene[index];
	}

	population.addSample(child1);
	population.addSample(child2);
}

void Algorithm::crossOverTwoPoint(Population & population, Sample parent1, Sample parent2)
{

	Sample child1 = Sample(parent1);
	Sample child2 = Sample(parent2);

	int startIndex = Utility::randomIndexGenerator(0, Utility::GENE_SIZE - Utility::CUT_LENGTH);

	for(int index=startIndex; index<startIndex + Utility::CUT_LENGTH; index++)
	{
		child1.gene[index] = parent2.gene[index];
		child2.gene[index] = parent1.gene[index];
	}

	population.addSample(child1);
	population.addSample(child2);
}

void Algorithm::crossOverUniform(Population & population, Sample parent1, Sample parent2)
{

	Sample child1 = Sample(parent1);
	Sample child2 = Sample(parent2);

	for(int index=0;index<Utility::GENE_SIZE;index++)
	{
		double random = Utility::randomValueGenerator();

		if(random < 0.5)
		{
			child1.gene[index] = parent2.gene[index];
			child2.gene[index] = parent1.gene[index];
		}
	}

	population.addSample(child1);
	population.addSample(child2);
}

vector<int> Algorithm::pmxCore(const vector<int> &p1, const vector<int> &p2, int cut1, int cut2)
{
	int n = (int)p1.size();
	int a = std::min(cut1, cut2);
	int b = std::max(cut1, cut2);

	vector<int> child(n, -1);
	vector<char> inSegment(n, 0);
	vector<int> posInP2(n, 0);
	for (int k = 0; k < n; k++) posInP2[p2[k]] = k;

	for (int i = a; i <= b; i++) { child[i] = p1[i]; inSegment[p1[i]] = 1; }

	for (int i = a; i <= b; i++)
	{
		int value = p2[i];
		if (inSegment[value]) continue;
		int pos = i;
		while (child[pos] != -1) pos = posInP2[p1[pos]];
		child[pos] = value;
	}

	for (int i = 0; i < n; i++)
		if (child[i] == -1) child[i] = p2[i];

	return child;
}

void Algorithm::crossOverPMX(Population &population, Sample parent1, Sample parent2)
{
	int n = Utility::GENE_SIZE;

	vector<int> p1(n), p2(n);
	for (int i = 0; i < n; i++) { p1[i] = parent1.gene[i].data; p2[i] = parent2.gene[i].data; }

	int cut1 = Utility::randomIndexGenerator(0, n - 1);
	int cut2 = Utility::randomIndexGenerator(0, n - 1);

	vector<int> c1 = pmxCore(p1, p2, cut1, cut2);
	vector<int> c2 = pmxCore(p2, p1, cut1, cut2);

	Sample child1 = Sample(parent1);
	Sample child2 = Sample(parent2);
	for (int i = 0; i < n; i++) { child1.gene[i].data = c1[i]; child2.gene[i].data = c2[i]; }

	population.addSample(child1);
	population.addSample(child2);
}

void Algorithm::crossOverWholeArithmeticRecombination(Population & population, Sample parent1, Sample parent2)
{

	Sample child1 = Sample(parent1);
	Sample child2 = Sample(parent2);

	for(int index=0;index<Utility::GENE_SIZE;index++)
	{
        child1.gene[index].data = Algorithm::alpha * parent2.gene[index].data + (1.0-Algorithm::alpha) * parent1.gene[index].data;
        child2.gene[index].data = Algorithm::alpha * parent1.gene[index].data + (1.0-Algorithm::alpha) * parent2.gene[index].data;
	}

	population.addSample(child1);
	population.addSample(child2);
}

Algorithm::~Algorithm(void)
{

}
