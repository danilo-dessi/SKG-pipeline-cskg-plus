import pandas as pd 
import os
from tqdm import tqdm
import ast
import urllib
import ast
import json
import pickle
import shutil



input_dir = './data/'
paper_info_dir = '../../data/processed/other_info/'
out_dir = './rdf_release/'

# for reification control variables
e2type = {}
obs_counter = 0
triple2stmid = {}
all_entities = []
#papers_in_graph = []



header = """
@prefix : <http://www.w3.org/2002/07/owl#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix cskg-ont: <https://w3id.org/cskg/ontology#> .
@prefix cskg: <https://w3id.org/cskg/resource/> .
@prefix dbpedia: <http://dbpedia.org/resource/> .
@prefix wikidata: <http://www.wikidata.org/entity/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix provo: <http://www.w3.org/ns/prov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""

		




if True:
	


	for file in tqdm(list(sorted(os.listdir(input_dir)))):
		######################### for csv release
		statement_id_column = []
		statement_frequency_column = []
		#########################

		if file[-4:] == '.csv':
			df = pd.read_csv(input_dir + file)
			#print(df.shape)
			df = df.dropna()
			df.drop(df.loc[(df['subj'] == 'learning_algorithm') & (df['obj'] == 'keywords')].index, inplace=True)
			#print(df.shape)
			#print('---')
			all_entities += df['subj'].tolist() + df['obj'].tolist()
			df.to_csv('csv_release/' + file, index=False) 
		else:
			continue
		
		fo = open(out_dir + file[:-4] + '.ttl', 'w+')
		fo_time = open(out_dir + 'time_' + file[:-4] + '.ttl', 'w+')
		fo.write(header)
		fo_time.write(header)

		subjs = []
		rels = []
		objs = []
		supports = []
		sources = []
		files = []
		#subj_types = []
		#obj_types = []
		#ndex(['Unnamed: 0', 'triple_id', 'subj', 'rel', 'obj', 'support', 'sources',
		#   'files', 'subj_type', 'obj_type', 'years'],
		#  dtype='object')

		removed_count = 0
		for i,r in df.iterrows():
			#########################  manual fix
			if str(r['subj']) == 'learning algorithm' and  str(r['obj']) == 'keywords':
				continue
			if str(r['subj']) == 'nan' or  str(r['obj']) == 'nan':
				continue
			removed_count += 1


			#########################

			subj = r['subj'] #urllib.parse.quote(str(r['subj']).replace(' ','_')) 	
			rel = r['obj_prop']
			obj = r['obj'] #urllib.parse.quote(str(r['obj']).replace(' ','_')) 
			sup = r['support']
			tools = ast.literal_eval(r['wasGeneratedBy'])
			papers = ast.literal_eval(r['wasDerivedFrom'])
			#stype = r['subj_type']	
			#otype = r['obj_type']
			years = ast.literal_eval(r['timeObservation'])	
			statement_id = r['triple_id']

			#e2type[subj] = stype
			#e2type[obj] = otype
			#papers_in_graph += list(papers)
			

			if rel != 'skos:broader':
				stm = '''
	cskg:statement_%d a cskg-ont:Statement,
			provo:Entity ;
		rdf:subject cskg:%s ;
		rdf:predicate cskg-ont:%s ;
		rdf:object cskg:%s ;
		cskg-ont:hasSupport "%d"^^xsd:integer ;'''%(statement_id, subj, rel, obj, sup)
				triple2stmid[(subj, rel, obj)] = statement_id
			else:
				stm = '''
	cskg:statement_%d a cskg-ont:Statement,
			provo:Entity ;
		rdf:subject cskg:%s ;
		rdf:predicate skos:broader ;
		rdf:object cskg:%s ;
		cskg-ont:hasSupport "%d"^^xsd:integer ;'''%(statement_id, subj, obj, sup)
				triple2stmid[(subj, rel, obj)] = statement_id


			paper_str = ''
			n_papers = len(papers)
			first = True
			for paper in papers:
				if first and n_papers == 1:
					paper_str += "\tprovo:wasDerivedFrom cskg:%s ;\n"%(paper)
					first = False
				elif first and n_papers > 1:
					paper_str += "\tprovo:wasDerivedFrom cskg:%s ,\n"%(paper)
					first = False
				else:
					paper_str += "\t\t cskg:%s ,\n"%(paper)
			paper_str = paper_str[:-2] + ';\n'

			tool_str = ''
			n_tools = len(tools)
			first = True
			for tool in tools:
				if first and n_tools == 1:
					tool_str += "\tprovo:wasGeneratedBy cskg:%s ;\n"%(tool.replace(' ','_'))
					first = False
				elif first and n_tools > 1:
					tool_str += "\tprovo:wasGeneratedBy cskg:%s ,\n"%(tool.replace(' ','_'))
					first = False
				else:
					tool_str += "\t\t cskg:%s ,\n"%(tool.replace(' ','_'))
			tool_str = tool_str[:-2] + ';\n'

			observations = ''
			n_observations = len(years)
			first = True
			for y,f in years:
				if first and n_observations == 1:
					observations += "\tcskg-ont:hasTimeObservation cskg:observation_statement_%d_%d ;\n"%(statement_id, y)
					first = False
				elif first and n_observations > 1:
					observations += "\tcskg-ont:hasTimeObservation cskg:observation_statement_%d_%d ,\n"%(statement_id, y)
					first = False
				else:
					observations += "\t\t cskg:observation_statement_%d_%d ,\n"%(statement_id, y)


			stm = stm + '\n'  + paper_str + tool_str + observations
			stm = stm[:-2] + '.\n'
			fo.write(stm)

			# years to statement
			for y,f in years:

				stm = '''
	cskg:observation_statement_%d_%d a cskg-ont:TimeObservation;
		cskg-ont:year "%d"^^rdfs:Literal ;
		cskg-ont:frequency "%d"^^xsd:integer .\n\n'''%(statement_id, y, y, f)
				fo_time.write(stm)


		fo.flush()
		fo.close()

		################# csv release files

		#df['statement_id'] = statement_id_column

		#df_stm_year = pd.DataFrame()
		######
		#df['rel'] = df['rel'].apply(lambda x: 'skos:broader' if x == 'skos:broader/is/hyponym-of' else x)

		#def adapat_rel(x):
		#	if x['rel'] != 'skos:broader':
		#		x['rel'] = x['rel'] + x['obj_type']
		#	return x
		#df = df.apply(adapat_rel)

		#df['subj'] = df['subj'].apply(lambda x: urllib.parse.quote(str(x).replace(' ','_')))
		#df['obj'] = df['obj'].apply(lambda x: urllib.parse.quote(str(x).replace(' ','_')))
		#########
		#df.drop(columns=['years', 'subj_type', 'obj_type'], inplace=True)
		#df.to_csv('csv_release/cskg_stm_' + file[:-4].split('_')[-1] +'.csv', index=False)	
		#print('csv_release/cskg_stm_' + file[:-4].split('_')[-1] +'.csv')
		#df_stm_year.to_csv('csv_release/cskg_stm_time_' + file[:-4].split('_')[-1] +'.csv', index=False)		


	with open('triple2stmid.pkl', 'wb') as f:
		pickle.dump(triple2stmid, f)

	print('>> General RDF created.')


if True:
	all_entities = set(all_entities)
	with open('../resources/e2dbpedia.pickle', 'rb') as f:
		e2dbpedia = pickle.load(f)

	with open(out_dir + 'dbpedia.ttl', 'w+') as fo:
		fo.write(header)
		links_turtle = ''
		for e, dbpedia in e2dbpedia.items():
			eurl = urllib.parse.quote(e.replace(' ','_')) 
			if eurl in all_entities:
				dbpedia = dbpedia.replace('http://dbpedia.org/resource/','')
				links_turtle += 'cskg:%s owl:sameAs dbpedia:%s'%(eurl,dbpedia) + ' .\n'
		fo.write(links_turtle)

	all_entities = set(all_entities)
	with open('../resources/e2wikidata.pickle', 'rb') as f:
		e2wikidata = pickle.load(f)

	with open(out_dir + 'wikidata.ttl', 'w+') as fo:
		fo.write(header)
		links_turtle = ''
		for e, wikidata in e2wikidata.items():
			eurl = urllib.parse.quote(e.replace(' ','_')) 
			if eurl in all_entities:
				wikidata = wikidata.replace('http://www.wikidata.org/entity/','')
				links_turtle += 'cskg:%s owl:sameAs wikidata:%s'%(eurl,wikidata) + ' .\n'
		fo.write(links_turtle)

	# CSVs
	dbpedia_df = pd.DataFrame()
	dbpedia_df['entity'] = [urllib.parse.quote(x.replace(' ','_')) for x in e2dbpedia.keys()]
	dbpedia_df['dbpedia_entity'] = e2dbpedia.values()
	dbpedia_df.to_csv('csv_release/dbpedia.csv', index=False)

	wikidata_df = pd.DataFrame()
	wikidata_df['entity'] = [urllib.parse.quote(x.replace(' ','_')) for x in e2wikidata.keys()]
	wikidata_df['wikidata_entity'] = e2wikidata.values()
	wikidata_df.to_csv('csv_release/wikidata.csv', index=False)


if True:
	all_entities = set(all_entities)
	df_type = pd.read_csv('entity_type.csv')
	df_type = df_type[df_type['entity'].isin(all_entities)]

	entities = df_type['entity'].tolist()
	types = df_type['type'].tolist()
	etypes = zip(entities, types)
	with open(out_dir + 'cskg_openalex_etypes.ttl', 'w+') as fo_types:
		fo_types.write(header)
		for e,t in etypes:
			fo_types.write("cskg:%s rdf:type cskg-ont:%s .\n"%(e,t))
	etypes = dict(etypes)

	df_type.to_csv('csv_release/entity_type.csv', index=False)

	print('>> Entity type RDF created.')	


if True:

	############## csv release
	stm_entities_df = pd.DataFrame()
	stm_statements_df = pd.DataFrame()

	stm_column = []
	stm_context = []

	##########################


	triple2stmid = None
	with open('triple2stmid.pkl', 'rb') as f:
		triple2stmid = pickle.load(f)

	#### adding context as entity set
	entities_context_df = pd.read_csv('contexts/entities_context.csv')
	triples = [tuple(ast.literal_eval(stm.replace('nan', '"nan"'))) for stm in entities_context_df['stm'].tolist()]

	#triples = [(urllib.parse.quote(str(s).replace(' ','_')), rel, urllib.parse.quote(str(o).replace(' ','_'))) for (s,rel,o) in triples]
	entities = entities_context_df['entities'].apply(lambda x: ast.literal_eval(x.replace('nan', '"nan"')))
	triple2connected_entities = dict(zip(triples, entities))
	
	fo_related_entities = open(out_dir + 'cskg_openalex_related_entities.ttl', 'w+')
	fo_related_entities.write(header)
	for t,entity_list in tqdm(triple2connected_entities.items()):
		#print(type(x), type(ast.literal_eval(x)))


		if t in triple2stmid:
			stm_number = triple2stmid[t]
		else:
			continue

		stm_conn_string = ''
		
		first = True
		entity_number = len(entity_list)

		for entity, cc in entity_list.items():
			#if cc >= 2:
				obs_str = '''
cskg:entity_observation_%d a cskg-ont:ContextEntityObservation;
	cskg-ont:relatedEntity cskg:%s ;
	cskg-ont:co-occurrence "%d"^^xsd:integer .\n\n'''%(obs_counter, urllib.parse.quote(str(entity).replace(' ','_')), cc)
				fo_related_entities.write(obs_str)
				
				stm_conn_string += '\t\t\t\tcskg:statement_%d cskg-ont:hasContextEntityObservation cskg:entity_observation_%d .\n'%(stm_number, obs_counter)
				obs_counter += 1
		fo_related_entities.write(stm_conn_string)

		stm_column += [stm_number]
		stm_context += [{entity : cc  for entity,cc in entity_list.items()}]
				

	fo_related_entities.flush()
	fo_related_entities.close()
	stm_entities_df['statementID'] = stm_column
	stm_entities_df['entity_context'] = stm_context
	stm_entities_df.to_csv('csv_release/stm_entity_context.csv', index=False)
	print('>> Entity Context RDF created.')	



	## adding context as statements
	statements_context_df = pd.read_csv('contexts/stm_context.csv')
	triples = [tuple(ast.literal_eval(stm.replace('nan', '"nan"'))) for stm in statements_context_df['stm'].tolist()]
	triples = [(urllib.parse.quote(str(s).replace(' ','_')), rel, urllib.parse.quote(str(o).replace(' ','_'))) for (s,rel,o) in triples]
	statements = statements_context_df['statements'].apply(lambda x: ast.literal_eval(x.replace('nan', '"nan"')))
	triple2connected_statements = dict(zip(triples, statements))

	stm_column = []
	stm_context = []

	fo_related_statements = open(out_dir + 'cskg_openalex_related_statements.ttl', 'w+')
	fo_related_statements.write(header)
	for t,statements_list in tqdm(triple2connected_statements.items()):
		#print(type(x), type(ast.literal_eval(x)))

		if t in triple2stmid:
			stm_number = triple2stmid[t]
		else:
			continue

		stm_conn_string = ''

		first = True
		statements_number = len(statements_list)

		#stm_context_new = {}
		for statement, cc in statements_list.items():

			if statement in triple2stmid: # and cc >= 2:
				stm_related_number = triple2stmid[statement]
			
				obs_str = '''
cskg:statement_observation_%d a cskg-ont:ContextStatementObservation;
	cskg-ont:relatedStatement cskg:statement_%d ;
	cskg-ont:co-occurrence "%d"^^xsd:integer .\n\n'''%(obs_counter, stm_related_number, cc)
				fo_related_statements.write(obs_str)

				stm_conn_string += '\t\t\t\tcskg:statement_%d cskg-ont:hasContextStatementObservation cskg:statement_observation_%d .\n'%(stm_number, obs_counter)
				#stm_context_new[stm_related_number] = cc

				obs_counter += 1
		fo_related_statements.write(stm_conn_string)
		stm_column += [stm_number]
		stm_context += [{statement : cc  for statement,cc in statements_list.items() if statement in triple2stmid}]


	stm_statements_df['statementID'] = stm_column
	stm_statements_df['statement_context'] = stm_context
	stm_statements_df.to_csv('csv_release/stm_statements_context.csv', index=False)
	fo_related_statements.flush()
	fo_related_statements.close()
	print('>> Statement Context RDF created.')	


if True:

	support_entities_df = pd.read_csv('support_entity.csv')
	support_entities_df = support_entities_df[support_entities_df['entity'].isin(all_entities)]
	#print(support_entities_df.shape)
	fo_entity_year_distribution = open(out_dir + 'cskg_entity_year_distribution.ttl', 'w+') 
	fo_entity_year_distribution.write(header)

	for i, r in tqdm(support_entities_df.iterrows()):
		e = r['entity']
		sup = r['support']

		#if e == 'nan' or sup < 100:
		#	continue
		if e not in all_entities or e == 'nan':
			continue
		e_conn_string = ''

		#e = urllib.parse.quote(str(e).replace(' ','_'))
		distribution = ast.literal_eval(r['years'])

		for y,f in distribution.items():
			estr = '''
cskg:entity_time_observation_%d a cskg-ont:TimeObservation;
	cskg-ont:year "%d"^^rdfs:Literal ;
	cskg-ont:frequency "%d"^^xsd:integer .\n\n'''%(obs_counter, y, f)

			fo_entity_year_distribution.write(estr)
			e_conn_string += 'cskg:%s cskg-ont:hasTimeObservation cskg:entity_time_observation_%d .\n'%(e,obs_counter)

			obs_counter += 1
		fo_entity_year_distribution.write(e_conn_string)

	fo_entity_year_distribution.flush()
	fo_entity_year_distribution.close()


	support_entities_df.to_csv('csv_release/entity_distribution.csv', index=False)
	print('>> Entity Distribution RDF created.')	


if True:

	paper_ids = []
	paper_years = []
	paper_doi = []

	papers_in_graph = []
	for file in tqdm(list(sorted(os.listdir(input_dir)))):
		df = pd.read_csv(input_dir + file)
		paper_column = df['wasDerivedFrom'].to_list()
		papers = [paper_id for paper_list in paper_column for paper_id in ast.literal_eval(paper_list)]
		
		papers_in_graph += papers
	papers_in_graph = set(papers_in_graph)
	print('n papers in graph:', len(papers_in_graph))

	with open(out_dir + 'paper_info.ttl', 'w+') as fo:
		fo.write(header)
		for paper_info in tqdm(list(os.listdir(paper_info_dir))):

			ttls = ''
			with open (paper_info_dir + paper_info, 'r') as f:
				for line in f:
					paper = json.loads(line)
					if paper['doc_key'] in papers_in_graph:
						paper_ids += [paper['doc_key']]
						paper_years += [paper['year']]
						paper_doi += [urllib.parse.quote(str(paper['doi']))]

						if paper['doi'] is not None:
							paper_ttl = '''
	cskg:%s a cskg-ont:Paper ;
		cskg-ont:year "%d"^^rdfs:Literal ;
		cskg-ont:doi "%s"^^xsd:anyURI .
				'''%(paper['doc_key'], paper['year'], urllib.parse.quote(str(paper['doi'])))

						else:
							paper_ttl = '''
	cskg:%s a cskg-ont:Paper ;
		cskg-ont:year "%d"^^rdfs:Literal .
				'''%(paper['doc_key'], paper['year'])

						ttls += paper_ttl
			fo.write(ttls)
			ttls = ''
	df = pd.DataFrame()
	df['paper'] = paper_ids
	df['year'] = paper_years
	df['doi'] = paper_doi
	df.to_csv('csv_release/paper_info.csv', index=False)



















