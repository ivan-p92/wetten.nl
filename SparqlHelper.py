'''
Created on 19 mei 2013

The purpose of this module is to retrieve data from doc.metalex.eu
through the sparql endpoint at doc.metalex.eu/sparql/

@author: Ivan
'''

# from xml.dom import minidom as mini
# import os
# import re
from xml.dom import minidom as mini
import urllib2
import pickle
import re

class SparqlHelper:
    
    def __init__(self):
        self.workDictionary = None
    
    def loadWorkDictionary(self):
        self.workDictionary = pickle.load(open('/Users/Ivan/Documents/Beta-gamma/KI jaar 2/Afstudeerproject/Project/Python/wetten.nl/works.pickle', 'r'))
    
    def getLatestDocForEntity(self, entity):
        """
        Returns the latest link to doc.metalex.eu/doc/<document> for the given work URI,
        where <document> is determined by the expression for the given work URI
        
        @param work: the work URI
        @return: string containing the latest expression
        """
        if not self.workDictionary:
            self.loadWorkDictionary()
            
        # Get work URI
        work = self.workDictionary[entity][0]
        
        # Get the latest expression
        expression =  self.getExpressionsForWork(work)[-1]
        
        # Replace /id/ by /doc/ and add /data.xml to the end
        doc = re.sub('eu/id/', 'eu/doc/', expression) + '/data.xml'
        
        return doc       
        
    def getExpressionsForWork(self, work):
        # Create sparql query
        query = 'PREFIX mo: <http://www.metalex.eu/schema/1.0#>SELECT DISTINCT * WHERE {?e mo:realizes <' + \
            work + '> }'
            
        # Pass query to sparql endpoint (through regular post request)
        data = urllib2.urlopen('http://doc.metalex.eu:8000/sparql/', 'query=' + query + '&soft-limit=-1')
        
        # Read xml and get results
        xml = mini.parseString(data.read())
        results = xml.getElementsByTagName('result')
        print 'Number of expressions: ' + str(results.length)
        
        # Extract the expression URI's from the results and add each to the
        # list of all expressions for this work
        expressions = []
        for result in results:
            bindings = result.getElementsByTagName('binding')
            expression = bindings[0].getElementsByTagName('uri')[0].firstChild.nodeValue
            expressions.append(expression)
        
        return expressions
        
def main():
    pass
    
    print '\nExecution ended'
if __name__ == '__main__':
    main()