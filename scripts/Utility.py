import rdflib
from rdflib import Graph, RDF, URIRef
from rdflib.namespace import NamespaceManager
import re

""" 
Read entire file content
* Input: file name
* Output: string with content read
"""
def readFile(filename):
	with open(filename) as f:
		content = f.read()
		return content


""" 
Parse the graph using RDFLib
* Input: file name, file format
* Output: parsed graph, exception in some RDF cases
"""
def parseGraph(filename, f):
	g = Graph()
	g = g.parse(filename, format = f)
	return g


""" 
Get used prefixes from RDF File using RDFLib
* Input: parsed graph from parseGraph()
* Output: list of used prefixes
"""
def getUsedPrefixesRDF(g):
	used_prefixes_p = [e.n3(g.namespace_manager).split(":")[0] for e in g.predicates(None, None)]
	used_prefixes_o = [e.n3(g.namespace_manager).split(":")[0] for e in g.objects(None, None)]
	used_prefixes = used_prefixes_p + used_prefixes_o
	#Remove duplicates
	used_prefixes = list(dict.fromkeys(used_prefixes))
	return used_prefixes


"""
Get declared prefixes from tll and shex files using regex
* Input: 
	* regex to extract the declared prefix entire line
	* regex to extract the URL from declared prefix line
	* splitter token for prefix name, ex.: "@prefix xsds: <http://url.org>" <- split token is ":"
	  "xmlns:rdf="http://www.w3.org/#"" <- split token is "="
* Output: list of declared prefixes
"""
def getDeclaredPrefixesRegex(content, regex_base, regex_url, split_char):
	prefixes = re.findall(regex_base, content)
	prefixes_list = []
	# print(prefixes)

	for p in prefixes:
		name = p.strip().split(split_char)[0]
		url = re.search(regex_url, p)
		prefixes_list.append((name, url[0]))
	return prefixes_list

""" 
Gets a list of declared prefixes and the file content to check for unused prefixes
* Input: list of declared prefixes, file content without header
* Output: list of unused prefixes
"""
def getUnusedPrefixesRegex(prefixes, content):
	#Get all expressions and check if prefix occurs
	error = False
	unused_prefixes = []

	for p in prefixes:
		rgx = p[0] + ':'
		rgx = re.compile(rgx)
		if rgx.search(content) == None:
			error = True
			unused_prefixes.append(p[0])
	
	#Remove xml and xds
	unused_prefixes = [x for x in unused_prefixes if all([x != 'xml', x != 'xsd', x != 'rdfs'])]

	return unused_prefixes

""" 
Gets a list of declared prefixes and a list of used prefixes to check for unused ones
* Input: list of declared prefixes, file content without header
* Output: list of unused prefixes
"""
def getUnusedPrefixesRDF(declared_prefixes, used_prefixes):
	#Remove used prefixes from declared prefixes list
	unused_prefixes = [x[0] for x in declared_prefixes if x[0] not in used_prefixes]

	#Remove xml and xds
	unused_prefixes = [x for x in unused_prefixes if all([x != 'xml', x != 'xsd', x != 'rdfs'])]

	return unused_prefixes

"""
Builds the error message
Input: list of unused prefixes
Output: string with all unused prefixes
"""
def getErrorMessage(p):
	msg = ''
	if len(p) > 0:
		for u in p:
			msg = msg + u + '\n'

	return msg

"""
Find duplicate prefixes (declaration or url) from list of declared prefixes
Input: list of declared prefixes
Output: list of duplicate prefixes
"""
def findDuplicates(prefixes):
	namespaces = [x[0] for x in prefixes]
	url = [x[1] for x in prefixes]

	dup_names = set([x for x in namespaces if namespaces.count(x) > 1])
	dup_urls = set([x for x in url if url.count(x) > 1])

	if(len(dup_names) > 0):
		return list(dup_names)
	elif(len(dup_urls) > 0):
		return list(dup_urls)
	else:
		return []