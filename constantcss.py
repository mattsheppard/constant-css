#!/usr/bin/python

import urllib
import re
import pprint
pp = pprint.PrettyPrinter(indent=4)

class CssWithConstants:
	data = None
	parameters = {}
	
	def __init__(self, url=None):
		# print url
		self.data = urllib.urlopen(url).read()
		# print data
		
		parameters = self.extract_parameters()
		
	def extract_parameters(self):
		# print self.data
		definition_blocks = re.compile('/\*\s*@cssconstants(.*?)\*/', re.S)
		groups = definition_blocks.search(self.data).groups()
		# pp.pprint(groups)
		for group in groups:
			definition_split_re = re.compile('@define')
			definitions = definition_split_re.split(group)
			for definition in definitions:
				marker_value_re = re.compile('^\s*(\w*)\s*(.*?)\s*$', re.S)
				pair = marker_value_re.search(definition).groups()
				# pp.pprint(pair)
				self.parameters[pair[0]] = pair[1];
		# pp.pprint(self.parameters)
		
	def final(self):
		result = self.data
		for key, value in self.parameters.iteritems():
			print key
			replacement = re.compile('/\*'+key+'\*/.*?/\*'+key+'\*/', re.S)
			result = replacement.sub('/*'+key+'*/'+value+'/*'+key+'*/',result)
		return result
		
def main():
	css = CssWithConstants('example.css')
	print css.final()

if __name__ == '__main__':
	main()
