import pandas as pd 
from tqdm import tqdm
import os
from collections import Counter
import ast
import pickle

idir = './data/'
out = 'support_entity.csv'
other_info_folder = '../../data/processed/other_info/'

entity2supportByYear = {}
already_seen = {}


paper2year = {}
try:
	with open('paper2year.pkl', 'rb') as f:
		paper2year = pickle.load(f)
except:
	for file in tqdm(os.listdir(other_info_folder)):
		with open(other_info_folder + file) as f:
			for line in f:
				line_dict = ast.literal_eval(line.replace("null", "''"))
				paper2year[line_dict['doc_key']] = line_dict['year']
				if line_dict['year'] <= 0:
					print('>> error in ', file, line_dict['doc_key'])

	with open('paper2year.pkl', 'wb') as f:
		pickle.dump(paper2year, f)

print('number of papers:', len(paper2year))

for file in tqdm(os.listdir(idir)):
		df = pd.read_csv(idir + file)
		df = df.dropna()
		for i,r in df.iterrows():
			papers = ast.literal_eval(r['wasDerivedFrom'])


			s = r['subj']
			if s not in entity2supportByYear:
				entity2supportByYear[s] = {}
				already_seen[s] = set()

			for paper in papers:
				if paper not in already_seen[s]:
					if paper in paper2year:
						year = paper2year[paper]
						already_seen[s].add(paper)

						if year not in entity2supportByYear[s]:
							entity2supportByYear[s][year] = 0 
						entity2supportByYear[s][year] += 1

			o = r['obj']
			if o not in entity2supportByYear:
				entity2supportByYear[o] = {}
				already_seen[o] = set()

			for paper in papers:
				if paper not in already_seen[s]:
					if paper in paper2year:
						year = paper2year[paper]
						already_seen[o].add(paper)

						if year not in entity2supportByYear[s]:
							entity2supportByYear[o][year] = 0 
						entity2supportByYear[o][year] += 1


edf = pd.DataFrame()
edf['entity'] = list(entity2supportByYear.keys())
edf['years'] = [dict(sorted(x.items())) for x in list(entity2supportByYear.values())]
edf['support'] = [sum(x.values()) for x in list(entity2supportByYear.values())]
edf.to_csv(out)















