import csv
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.util import bigrams
from os import listdir
from os.path import join, isfile
import pickle
import math

def index(input_file, output_file_dictionary, output_file_postings):
	
	# List of document_ids of all docs
	doc_ids = []
	# Map document_id to dictionaries of documents
	documents = {}
	
	# Store each document as a dictionary whose keys are the fields
	# of the document.
	with open(input_file, "r") as csv_file:
		csv_reader = csv.DictReader(csv_file)
		line_count = 0
		for row in csv_reader:
			doc_ids.append(int(row['document_id']))
			documents[str(row['document_id'])] = row
			# print(doc_ids[line_count])
			# print(documents[str(row['document_id'])])
			line_count += 1
	
	doc_ids.sort()

	# Every term in the dictionary is mapped to a tuple (byte_offset, doc_freq)
	dictionary = {}
	# Every term in the index is mapped to a postings list
	index = {}
	# Every doc_id is mapped to document vector length
	lengths = {}

	# For every term in every document, add the document_id of the occuring term
	# to the respective posting list in the index. If term is new, add new key 
	# in dictionary and index
	for doc_id in doc_ids:
		# Combine all fields in doc into one text
		document = documents[str(doc_id)]
		text = ""
		for field in document:
			text = " ".join((text, document[field]))
		#### Preprocess Text ###
		text = text.replace('\n', ' ')
		# tokenize
		sentences = sent_tokenize(text)
		
		
		# Replace all non-alphanum, non-space chars in each sentence with space
		tokens = []
		for sent in sentences:
			new_sent = []  
			for c in sent:
				if c.isalnum() or c.isspace():
					new_sent.append(c)
				else: 
					new_sent.append(' ')
			sent = ''.join(new_sent)
			tokens.extend([token.lower() for token in word_tokenize(sent)])	
		
		# stem the tokens
		ps = nltk.stem.PorterStemmer()
		stemmed_tokens = [ps.stem(token) for token in tokens]
		
		# Augment list of tokens with 2-word and 3-word phrases
		#for bigram in bigrams(stemmed_tokens):
			

		# maps every unique term in doc to its frequency
		term_to_freq = {}
		for term in stemmed_tokens:
			if term not in dictionary:
				dictionary[term] = (None, 1)
				index[term] = [(doc_id, 1)]
				term_to_freq[term] = 1	
			# if doc_id is not already added to term's postings
			elif index[term][dictionary[term][1]- 1][0] != doc_id: 
				# increment df for term
				dictionary[term] = (None, dictionary[term][1] + 1)
				index[term].append((doc_id, 1))
				term_to_freq[term] = 1	
			# if doc_id is already added to term's postings, increment tf for that document
			else:
				index[term][dictionary[term][1] - 1] = (index[term][dictionary[term][1] - 1][0], index[term][dictionary[term][1] - 1][1] + 1)
				term_to_freq[term] += 1	
				#print("Increment tf of " + term + " in " + str(doc_id) + " to " + str(posting[1]))
		
		# calculate and store vector magnitude of doc
		mag_square = 0
		for term in term_to_freq:
			mag_square += math.pow(1 + math.log10(term_to_freq[term]),2)
		vector_len = math.sqrt(mag_square)
 		lengths[doc_id] = vector_len

	# Add skip pointers to every postings list
	for term in index:
		doc_freq = dictionary[term][1]
		skip_pointers_count = int(math.sqrt(doc_freq))
		skip_size = int(doc_freq / skip_pointers_count)
		for i in range(0, (doc_freq - skip_size - 1)):
			if i % skip_size == 0:
				index[term][i] = (index[term][i][0], index[term][i][1], i + skip_size)

	# Write dictionary and index
	offset = 0
	postings_file = open(output_file_postings, "w")
	sorted_terms = dictionary.keys()
	sorted_terms.sort()
	
	# Write all document ids at top of postings file
	postings_file.write(str(doc_ids) + '\n')	
	offset = postings_file.tell()

	# Write index to postings file and corresponding
        # byte offset to dictionary file
	for k in sorted_terms:
		dictionary[k] = (offset,dictionary[k][1])
		postings_file.write(str(index[k]) + '\n')
		offset = postings_file.tell()
	postings_file.flush()
	postings_file.close()

	for term in index:
		print(term)
		print(index[term])

	# Write dictionary to dictionary file			
	dictionary_file = open(output_file_dictionary, "wb")
	pickle.dump(dictionary, dictionary_file)		
	dictionary_file.flush()
	dictionary_file.close()

	# Write document vector lengths to lengths file
	lengths_file = open("lengths.txt", "wb")
	pickle.dump(lengths, lengths_file)
	lengths_file.flush()
	lengths_file.close()

				
	
	
	
	




