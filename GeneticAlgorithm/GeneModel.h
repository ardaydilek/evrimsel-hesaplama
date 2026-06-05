#ifndef GENE_MODEL_H_
#define GENE_MODEL_H_

class GeneModel
{
public:
	friend class Sample;

	int data;

	GeneModel(void);
	GeneModel(int city);
	~GeneModel(void);
};

#endif
