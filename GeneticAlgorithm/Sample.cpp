#include "Sample.h"

Sample::Sample()
{
	if (Utility::GENE_SIZE == 0)
	{
		cout << "Error: Gene size cannot be zero!" << endl;
		exit(-1);
	}
	gene.reserve(Utility::GENE_SIZE);
	sampleID = 0;
	fitness = 0.0;
	normalizedFitness = 0.0;
	accumulatedFitness = 0.0;
	tourLength = 0.0;
}

Sample::Sample(const Sample &sample)
{
	gene.reserve(Utility::GENE_SIZE);
	sampleID = sample.sampleID;
	fitness = sample.fitness;
	normalizedFitness = sample.normalizedFitness;
	accumulatedFitness = sample.accumulatedFitness;
	tourLength = sample.tourLength;
	for (int i = 0; i < (int)sample.gene.size(); i++)
		gene.push_back(sample.gene[i]);
}

void Sample::setSample(vector<GeneModel> sampleGene)
{
	gene.clear();
	for (int i = 0; i < (int)sampleGene.size(); i++)
		gene.push_back(sampleGene[i]);
}

void Sample::initRandomTour()
{
	gene.clear();
	for (int city = 0; city < Utility::GENE_SIZE; city++)
		gene.push_back(GeneModel(city));

	for (int i = Utility::GENE_SIZE - 1; i > 0; i--)
	{
		int j = Utility::randomIndexGenerator(0, i);
		std::swap(gene[i], gene[j]);
	}
}

double Sample::getFitness() { return fitness; }
double Sample::getNormalizedFitness() { return normalizedFitness; }
double Sample::getTourLength() { return tourLength; }
void Sample::setFitness(double f) { this->fitness = f; }
void Sample::setNormalizedFitness(double nf) { this->normalizedFitness = nf; }

void Sample::mutate()
{

	if (Utility::randomValueGenerator() >= Utility::MUTATION_RATE)
		return;

	int n = Utility::GENE_SIZE;
	int a = Utility::randomIndexGenerator(0, n - 1);
	int b = Utility::randomIndexGenerator(0, n - 1);
	if (a > b) std::swap(a, b);

	if (Utility::MUTATION == Utility::SWAP)
	{
		std::swap(gene[a], gene[b]);
	}
	else
	{
		while (a < b) { std::swap(gene[a], gene[b]); a++; b--; }
	}
}

vector<int> Sample::tourAsCityIds() const
{
	vector<int> ids;
	ids.reserve(gene.size());
	for (int i = 0; i < (int)gene.size(); i++)
		ids.push_back(gene[i].data + 1);
	return ids;
}

void Sample::printSample()
{
	printf("ID:%d (len=%.1f): ", sampleID, tourLength);
	for (int i = 0; i < (int)gene.size(); i++)
		printf("%d ", gene[i].data + 1);
	cout << endl;
}

Sample::~Sample(void) { gene.clear(); }
