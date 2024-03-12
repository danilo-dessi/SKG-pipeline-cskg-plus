# SKG-pipeline-cskg-plus

The repository contains the additional scripts and files to re-build CS-KG 2.0. 

The paper accompanying this repository is still under review. The details will be disclosed after the paper acceptance.


## How to use

The pipeline in this github repository is a variant to work with OpenAlex data of [SKG-pipeline](https://github.com/danilo-dessi/SKG-pipeline). Here you can find the steps you can follow on your data. 

**Note:** We can only provide a sample of the data to test the pipeline. The full data belongs to [OpenAlex](https://openalex.org/). The sample of data contains research papers that were randomly selected.

### Data preparation 

1. Add your [OpenAlex](https://openalex.org/) data under data/original. The repository provides an example. More than one .jsonl file can be added to this directory. 

2. Go in src/extraction and run ```python preprocess.py```.

### Extraction process 

Go to **/src/extraction/** and execute:

1. ```python data_preparation_dygiepp.py```

2. ```./run_dygiepp.sh```

3. ```./run_corenlp.sh```

Missing output folders will be automatically created.

### Triples Generation

This part of the pipeline will clean and merge the entities, will map the entities to external resources, will map the verbs and will create a set of triples that needs to be validated by the next steps before to create the final knowledge graph.


Go to **/src/construction/** and execute:

```python cskg_construction.py ```


### Triples Validation

Go to **/src/transformer/** and execute to prepare the triple for the validation step:

1. Download the model (*tuned-transformer.zip*) from https://zenodo.org/record/6628472#.YqIH_-xBw6A and save it under **/src/transformer/tuned-transformer/**

2. To apply the model on the triples accordingly to predefined thresholds in our paper you can run: ```python applyModel.py tuned-transformer/ 3 3```. The command has as interface ```python applyModel.py MODEL_NAME SUPPORT_S1 SUPPORT_S2``` where:
	
	1. *MODEL_NAME* is the model saved under *./tuned-transformer/*

	2. *SUPPORT_S1* and *SUPPORT_S2* are the two thresholds you can use to select the reliable triples for the finetunig step to select which triples must be validated.


Alternatively, if you prefer to finetune the SciBERT transformer model on other data while executing this pipeline you can do as follows:

1. ```python prepareTrainingData.py SUPPORT_S1 SUPPORT_S2```

2. To finetune the SciBERT transformer model on new data you must execute ```python finetuner.py``` which will save the model under *./tuned-transformer/*.

3. Apply the model on the triples accordingly to predefined thresholds by using: ```python applyModel.py MODEL_NAME SUPPORT_S1 SUPPORT_S2```

### Mapping to the Ontology

1. Go in *schema_validation/*.

2. Run ``python apply_onto.py```.

### Add context and time information

1. Go in *postprocessing/*.

2. Run *python 1_triple_selector.py*.

3. Run *python 2_context.py*.

4. Run *python 3_compute_support_entity.py*.

5. Run *python create_rdf.py*.

The resulting CSV and Turtle files can be found under *csv_release/* and *rdf_release/* sub-folders that are automatically created.



## The Computer Science Knowledge Graph

The user of this github repository can access to the dump of the created resource, its sparql endpoint, and additional material through a dedicated [website](https://scholkg.kmi.open.ac.uk/).


## Contact
For inquiries about the pipeline, please contact Danilo Dessi' at danilo.dessi@unica.it. Please note that all the code has been tested with python 3.9 and that we do not provide support to install libraries and dependencies that do not depend on us within your environment.











