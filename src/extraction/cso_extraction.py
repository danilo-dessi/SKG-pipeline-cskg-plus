from cso_classifier import CSOClassifier 
import os
from tqdm import tqdm
import json
#cc.setup()
#exit() # it is important to close the current console, to make those changes effective


input_dir = '../../data/processed/dygiepp_input/'
output_dir = '../../data/processed/cso_output/'

if not os.path.exists(output_dir):
	os.makedirs(output_dir)


files = set(os.listdir(input_dir))
already_processed_files = set(os.listdir(output_dir))
files = list(files - already_processed_files)
print('>> Files to process:', len(files))

cc = CSOClassifier(workers = 5, modules = "both", enhancement = "no", explanation = False)

for file in files:
	print('>> processing:', file)
	papers = {}
	with open(input_dir+file, 'r') as fr:
		lines = list(fr)
		for  line in tqdm(lines):
			paper_data = json.loads(line)
			#print(paper_data)
			
			papers[paper_data['doc_key']] = {}
			papers[paper_data['doc_key']]['title'] = ' '.join(paper_data['sentences'][0])

			abstract = ' '.join([x for sentence in paper_data['sentences'][1:] for x in sentence])
			papers[paper_data['doc_key']]['abstract'] = abstract

	result = cc.batch_run(papers)
	#print(result)
				
	with open(output_dir+file, 'w+') as fw:
		for key, items in result.items():
			dump_data = dict(items)
			dump_data['doc_key'] = key
			json.dump(dump_data, fw)
			fw.write('\n')
