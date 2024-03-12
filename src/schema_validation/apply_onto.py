import pandas as pd
import os
from tqdm import tqdm




def load_onto_rules():
	onto_rules = pd.read_csv('../resources/onto-design-table-CSKG.csv')
	validDomainRelRange = set()
	for i, row in onto_rules.iterrows():
		kind_s = row['subj']
		kind_o = row['obj']
		rel = row['rel']
		validity = row['valid'] == 'y'
		transitive = row['transitivity']

		if rel != 'skos:broader/is/hyponym-of' and validity:
				validDomainRelRange.add((kind_s, rel, kind_o))

	return validDomainRelRange



def validateDataframe(df, validDomainRelRange):

	validated_df = pd.DataFrame()
	list_valid = []
	discarded_by_onto = []
	for i,r in df.iterrows():
		s = r['subj']
		rel = r['rel']
		o = r['obj']
		sup = int(r['support'])
		tools = r['sources']
		sources_len = r['source_len']
		files = r['files']
		stype = r['subj_type']
		otype = r['obj_type']

		if (stype, rel + otype, otype) in validDomainRelRange or (rel == 'skos:broader/is/hyponym-of' and stype == otype) or rel=='conjunction':
				#validated_df = pd.concat([validated_df, r.to_frame().T], ignore_index=True)
				list_valid += [r]
		else:
			discarded_by_onto += [r]
	validated_df = pd.DataFrame(list_valid)
	discarded_by_onto_df = pd.DataFrame(discarded_by_onto)
	return validated_df, discarded_by_onto_df


if __name__ == '__main__':
	validDomainRelRange = load_onto_rules()
	new_file_number = 0

	count = 0
	folder = '../transformer/'
	for file in tqdm([x for x in os.listdir(folder) if 'reliable' in x]):
		#print('>> file:%s'%(file))
		df = pd.read_csv(folder + file)
		#print('\t> shape df:', df.shape)
		validated_df, discarded_by_onto_df = validateDataframe(df, validDomainRelRange)
		#print('\t> shape validated df', validated_df.shape)
		count += validated_df.shape[0]
		if validated_df.shape[0] > 0:
			validated_df.to_csv('cskg_openalex_triples_%d.csv'%(new_file_number))
			new_file_number += 1
		if discarded_by_onto_df.shape[0] > 0:
			discarded_by_onto_df.to_csv('discarded_cskg_openalex_triples_%d.csv'%(new_file_number))
		#print('------------------\n')

	print('>> reliable triples ok for ontology:', count)

	for file in tqdm([x for x in os.listdir(folder) if 'classified' in x]):
		#print('>> file:%s'%(file))
		df = pd.read_csv(folder + file)
		df = df[df['predicted_labels'] == 1]
		#print('\t> shape df:', df.shape)
		validated_df, discarded_by_onto_df = validateDataframe(df, validDomainRelRange)

		#print('\t> shape validated df', validated_df.shape)
		count += validated_df.shape[0]
		if validated_df.shape[0] > 0:
			#validated_df.to_csv('cskg_openalex_triples_%d.csv'%(new_file_number))
			new_file_number += 1
		#print('------------------\n')
		if discarded_by_onto_df.shape[0] > 0:
			discarded_by_onto_df.to_csv('discarded_cskg_openalex_triples_%d.csv'%(new_file_number))
	print('>> total triples ok for ontology:', count)










