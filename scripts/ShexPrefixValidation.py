import re
import glob
import logging
import sys
import Utility as utility

# set log level
logging.basicConfig(level=logging.INFO)

root_path = "../"

for filename in glob.iglob(root_path+ '**/*.shex', recursive=True):
		logging.info("Validating Shex file " + filename)
		try:
			#Read File
			content = utility.readFile(filename)

			#Get Declared prefixes
			declared_prefixes = utility.getDeclaredPrefixesRegex(content, r'PREFIX(.*?) \n', r'\<(.*?)\>', ":")

			#Check redundant declaration
			duplicated_prefixes = utility.findDuplicates(declared_prefixes)
			
			#If so, raise exception
			if len(duplicated_prefixes) > 0:
				msg = utility.getErrorMessage(duplicated_prefixes)
				raise Exception("Duplicated prefix declaration: {}".format(msg))

			#Remove prefixes from content
			content = re.sub(r'PREFIX(.*?)\n', '', content)

			#Check for prefix usage
			unused_prefixes = utility.getUnusedPrefixesRegex(declared_prefixes, content)

			#If at least one of them have not been used, raise exception
			if len(unused_prefixes) > 0:
				msg = utility.getErrorMessage(unused_prefixes)
				raise Exception("Unused prefixes:\n {}".format(msg))
		except Exception as e:
				logging.error(e)
				logging.error("Syntaxic error reading turtle file [" +filename+"]")
				sys.exit(1)

print("RDF files syntaxic validation is successful")