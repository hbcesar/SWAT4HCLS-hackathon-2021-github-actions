import glob
import logging
from rdflib import Graph
import sys

# set log level
logging.basicConfig(level=logging.INFO)

root_path = "../"

rdf_file_extension = {".ttl":"turtle", ".nt":"nt", ".rdf":"application/rdf+xml"}

for extension in rdf_file_extension.keys() :
    files_to_check = "**/*" + extension
    for filename in glob.iglob(root_path + files_to_check, recursive=True):
         logging.info("Validating rdf file " + filename)
         try:
             graph = Graph()
             graph.parse(filename, format = rdf_file_extension[extension])
         except Exception as e:
             logging.error(e)
             logging.error("Syntaxic error reading the rdf file [" +filename+"]")
             sys.exit(1)

logging.info("RDF files syntaxic validation is successful. No syntaxic errors are found.")