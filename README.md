# SKG-pipeline-cskg-plus

The repository contains the additional scripts and files to re-build CS-KG 2.0. 

The paper accompanying this repository is still under review. The details will be disclosed after the paper acceptance.


## How to use

1. Download the [OpenAlex](https://openalex.org/) data and use it within the pipeline described in [SKG-pipeline](https://github.com/danilo-dessi/SKG-pipeline)

2. Run the pipeline [SKG-pipeline](https://github.com/danilo-dessi/SKG-pipeline) **without** mapping the data to the ontology.

3. Replace the directory *rdfmaker/* with the one in this repository.

4. Run ``python apply_onto.py```.

5. Add *postprocessing/* to your project and add the *other_info* files available [here]() run the python files ```1_triple_selector.py```, ```2_context.py```, ```3_compute_support_entity.py```, ```4_create_rdf.py```.



## Contact
For inquiries about the pipeline, please contact Danilo Dessi' at danilo.dessi@unica.it. Please note that all the code has been tested with python 3.9 and that we do not provide support to install libraries and dependencies that do not depend on us within your environment.











