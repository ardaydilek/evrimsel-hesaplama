#include "Population.h"

Population::Population(void)
{
	if(Utility::POPULATION_SIZE == 0)
	{
		cout<<"Error: Population size cannot be zero!"<<endl;
		exit(-1);
	}

}

Sample Population::getFittest()
{
	return sampleList[0];
}

void Population::addSample(Sample & sample)
{
	sample.sampleID = Utility::ID_COUNTER++;
	sampleList.push_back(Sample(sample));
}

bool sampleCompare(Sample & s1, Sample & s2)
{
	return (s1.getFitness() > s2.getFitness());
}

void Population::sort()
{
	std::sort(sampleList.begin(), sampleList.end(), sampleCompare);
}

void Population::cleanUp()
{
	if( sampleList.size() > Utility::POPULATION_MAX_SIZE)
	{
		while(sampleList.size() > Utility::POPULATION_MAX_SIZE)
			sampleList.erase(sampleList.end()-1);
	}
}

void Population::printSampleFitnesses()
{
	cout<<"Sample list:"<<endl;

	vector<Sample>::iterator it;

	for(it = sampleList.begin(); it != sampleList.end(); ++it)
	{
		printf("%d: %f, ", it->sampleID, it->fitness);
	}

	cout<<endl;
}

void Population::printSampleDetail()
{
	cout<<"Sample list:"<<endl;

	vector<Sample>::iterator it;

	for(it = sampleList.begin(); it != sampleList.end(); ++it)
	{
		it->printSample();
	}

	cout<<endl;
}

Population::~Population(void)
{
	sampleList.clear();
}
