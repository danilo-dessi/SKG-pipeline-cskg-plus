## Used to merge files and remove duplicate subj, rel, obj

import pandas as pd 
import os 
from tqdm import tqdm
import ast
import pickle
import urllib

triple_dir = '../rdfmaker/'
out_dir = 'data/'
other_info_folder = 'other_info/'
out_counter = 0
seen = set()
index_id = 0
e2type = {}

def check(x):
	return (x['subj'], x['rel'], x['obj']) in seen

def create_obj_prop(x):
	if x['rel'] == 'skos:broader/is/hyponym-of':
		return 'skos:broader'
	return x['rel'] + e2type[x['obj']]

def urler(x):
	return urllib.parse.quote(str(x).replace(' ','_')) 	



paper2year = {}
try:
	with open('paper2year.pkl', 'rb') as f:
		paper2year = pickle.load(f)
except:
	for file in tqdm(os.listdir(other_info_folder)):
		with open(other_info_folder + file) as f:
			for line in f:
				#print(line.replace("null", "''"))
				line_dict = ast.literal_eval(line.replace("null", "''"))
				paper2year[line_dict['doc_key']] = line_dict['year']
				if line_dict['year'] <= 0:
					print('>> error in ', file, line_dict['doc_key'])

	with open('paper2year.pkl', 'wb') as f:
		pickle.dump(paper2year, f)
print('n papers:', len(paper2year))


df = pd.DataFrame()
for file in tqdm(list(sorted(os.listdir(triple_dir)))):
	if file[-4:] == '.csv':
		df_temp = pd.read_csv(triple_dir + file)
		df_temp['subj'] = df_temp['subj'].apply(urler)
		df_temp['obj'] = df_temp['obj'].apply(urler)
		#print(df_temp.head(5))
		subjs = df_temp['subj'].tolist()
		rels = df_temp['rel'].tolist()
		objs = df_temp['obj'].tolist()
		triples = zip(subjs,rels,objs)

		# check for duplicates and remove
		n1 = df_temp.shape[0]
		df_temp['val'] = df_temp.apply(check, axis=1)
		df_temp = df_temp.drop(df_temp[df_temp['val'] == True].index)
		n2 = df_temp.shape[0]
		seen.update(triples)

		#### entity types
		subjs = df_temp['subj'].tolist()
		objs = df_temp['obj'].tolist()
		stypes = df_temp['subj_type'].tolist()
		otypes = df_temp['obj_type'].tolist()
		stypes = zip(subjs, stypes)
		otypes = zip(objs, otypes)

		for e, t in list(stypes) + list(otypes):
			if e not in e2type:
				e2type[e] = t

		### adding year info
		triple_years = []
		for i,r in df_temp.iterrows():
			years = {}
			for paper in ast.literal_eval(r['files']):
				#print(paper)
				if paper in paper2year:
					if paper2year[paper] not in years:
						years[paper2year[paper]] = 0	
					years[paper2year[paper]] += 1
				else:
					print('# paper %s not found'%(paper))
			years_sorted = sorted(years.items())
			#print((r['subj'], r['rel'], r['obj'], r['files']), years_sorted)
			triple_years += [years_sorted]
		df_temp['timeObservation'] = triple_years

		## creating object properties
		df_temp['obj_prop'] = df_temp.apply(create_obj_prop, axis=1)

		## rename colums
		df_temp = df_temp.rename(columns={'files' : 'wasDerivedFrom', 'sources': 'wasGeneratedBy'})


		## concat
		df = pd.concat([df,df_temp], ignore_index=True)
		if df.shape[0] >= 2000000:
			df['triple_id'] = range(index_id, index_id + len(df))
			index_id += len(df)
			df = df.drop(['val', 'predicted_labels', 'source_len', 'subj_type', 'obj_type'], axis=1)
			df.to_csv(out_dir + 'cskg_data_' + str(out_counter) + '.csv', index=False)
			out_counter += 1
			df = pd.DataFrame()



# save entity types
entities = e2type.keys()
types = e2type.values()
df = pd.DataFrame()
df['entity'] = entities
df['type'] = types
df.to_csv('entity_type.csv')


