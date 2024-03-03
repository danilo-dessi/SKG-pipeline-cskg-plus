import pandas as pd
import os
from tqdm import tqdm
import ast
import json


d = './data/'
high_stm = []
support_th = 5
paper2stm = {}
stm2paper = {}
stm2support = {}
entity2paper = {}
paper2entity = {}
seen = set()
#print(list(sorted(os.listdir(d))))
for file in tqdm(list(sorted(os.listdir(d)))):
		df = pd.read_csv(d + file)

		for i, r in df.iterrows():
			s = r['subj']
			p = r['obj_prop']
			o = r['obj']

			if str(r['subj']) == 'learning algorithm' and  str(r['obj']) == 'keywords': #hard-coded bug fix
				continue
			if str(r['subj']) == 'nan' or  str(r['obj']) == 'nan':
				continue

			papers = list(ast.literal_eval(r['wasDerivedFrom']))
			support = r['support']

			if (s,p,o) not in stm2paper:
				stm2paper[(s,p,o)] = []
			stm2paper[(s,p,o)] += papers
			stm2support[(s,p,o)] = len(papers)

			for paper in papers:
				if paper not in paper2stm:
					paper2stm[paper] = []
				paper2stm[paper] += [(s,p,o)]

				if paper not in paper2entity:
					paper2entity[paper] = []
				paper2entity[paper] += [s]
				paper2entity[paper] += [o]

			if s not in entity2paper:
				entity2paper[s] = set()
			entity2paper[s].update(papers)
			
			if o not in entity2paper:
				entity2paper[o] = set()
			entity2paper[o].update(papers)


			if support >= support_th and (s,p,o) not in seen:
				high_stm += [(s,p,o)]
				seen.add((s,p,o))

print('number of statements of openalex_kg', len(stm2paper))
print('number of papers of openalex_kg', len(paper2stm))
print('number of statements with high support of openalex_kg', len(high_stm))

stms = []
stms_support_list = []
entities_lists = []
entities_lists_count = []


for (s,p,o) in tqdm(high_stm):
	papers = set(stm2paper[(s,p,o)])
	#print((s,p,o))

	entities = {}
	for paper in papers:
		for e in set(paper2entity[paper]):
			if e != s and e != o:
				if e not in entities:
					entities[e] = 0
				entities[e] += 1
	#print(entities, len(entities))

	stms += [(s,p,o)]
	stms_support_list += [stm2support[(s,p,o)]]

	entities_lists += [dict(list(sorted(entities.items(),  key=lambda x :x[1], reverse=True))[:30])]
	entities_lists_count += [len(entities)]


	if len(stms) % 1000 == 0:
		df = pd.DataFrame({'stm' : stms, 'support':stms_support_list, 'n_entities': entities_lists_count, 'entities' : entities_lists})
		df.to_csv('contexts/entities_context.csv')

df = pd.DataFrame({'stm' : stms,  'support':stms_support_list, 'n_entities': entities_lists_count, 'entities' : entities_lists})
df.sort_values(by='support', inplace=True, ascending=False)
df.to_csv('contexts/entities_context.csv')
#df.to_excel('contexts/entities_context.xlsx')

stms = []
stms_support_list = []
stms_list = []
stms_list_count = []

for (s,p,o) in tqdm(high_stm):
	papers = set(stm2paper[(s,p,o)])

	statements = {}
	for paper in papers:
		for (s1,p1,o1) in set(paper2stm[paper]):
			if (s1,p1,o1) != (s,p,o):
				if (s1,p1,o1) not in statements:
					statements[(s1,p1,o1)] = 0
				statements[(s1,p1,o1)] += 1

	stms += [(s,p,o)]	
	stms_support_list += [stm2support[(s,p,o)]]

	stms_list += [dict(list(sorted(statements.items(),  key=lambda x :x[1], reverse=True))[:30])]
	stms_list_count += [len(statements)]

	if len(stms) % 1000 == 0:
		df = pd.DataFrame({'stm' : stms, 'support':stms_support_list, 'n_statements': stms_list_count, 'statements' : stms_list})
		df.to_csv('contexts/stm_context.csv')

df = pd.DataFrame({'stm' : stms, 'support':stms_support_list, 'n_statements': stms_list_count, 'statements' : stms_list})
df.sort_values(by='support', inplace=True, ascending=False)
df.to_csv('contexts/stm_context.csv')
#df.to_excel('contexts/stm_context.xlsx')









