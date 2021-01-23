#Checks if all declared prefixes are used in the RDF File

import glob
import logging
import sys
import Utility as utility
import re

# set log level
logging.basicConfig(level=logging.INFO)

root_path = "../"

rdf_file_extension = {".ttl":"turtle", ".nt":"nt", ".rdf":"application/rdf+xml"}
regex_prefix = {".ttl": r'@prefix(.*?)\n', ".rdf": r'xmlns:(.*?)\n'}
regex_url = {".ttl": r'\<(.*?)\>', ".rdf": r'\"(.*?)\"'}
regex_splitter = {".ttl": ":", ".nt":"nt", ".rdf":"="}

for extension in rdf_file_extension.keys() :
	files_to_check = "**/*" + extension
		
	for filename in glob.iglob(root_path + files_to_check, recursive=True):
		logging.info("Validating file " + filename)

		try:
			#Parse file using rdflib
			g = utility.parseGraph(filename, rdf_file_extension[extension])

			#Read File
			content = utility.readFile(filename)

			#Get Declared prefixes
			declared_prefixes = utility.getDeclaredPrefixesRegex(content, regex_prefix[extension], regex_url[extension], regex_splitter[extension])

			#Check redundant declaration
			duplicated_prefixes = utility.findDuplicates(declared_prefixes)
			
			#If redundant, raise exception
			if len(duplicated_prefixes) > 0:
				msg = utility.getErrorMessage(duplicated_prefixes)
				raise Exception("Duplicated prefix declaration: {}".format(msg))

			if(extension == '.ttl'):
				#Remove prefixes from content
				content = re.sub(r'@prefix(.*?)\n', '', content)

				#Check for prefix usage
				unused_prefixes = utility.getUnusedPrefixesRegex(declared_prefixes, content)

			elif(extension == '.rdf'):
				#Check for prefix usage
				used_prefixes = utility.getUsedPrefixesRDF(g)
				unused_prefixes = utility.getUnusedPrefixesRDF(declared_prefixes, used_prefixes)

			#If there are unused prefixes, raise exception
			if len(unused_prefixes) > 0:
				msg = utility.getErrorMessage(unused_prefixes)
				raise Exception("Unused prefixes:\n {}".format(msg))

		except Exception as e:
				logging.error(e)
				logging.error("Syntaxic error reading turtle file [" +filename+"]")
				sys.exit(1)

print("Files syntaxic validation is successful")
