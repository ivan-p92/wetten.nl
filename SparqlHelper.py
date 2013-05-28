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
import datetime

class SparqlHelper:
    
    def __init__(self):
        self.workDictionary = None
        self.months = ['', ' januari ', ' februari ', ' maart ',
                       ' april ', ' mei ', ' juni ', ' juli ',
                       ' augustus ', ' september ', ' oktober ',
                       ' november ', ' december ']
    
    def loadWorkDictionary(self):
        self.workDictionary = pickle.load(open('/Users/Ivan/Documents/Beta-gamma/KI jaar 2/Afstudeerproject/Project/Python/wetten.nl/works.pickle', 'r'))
    
    def getLatestDocForEntity(self, entity):
        """
        Returns the latest link to doc.metalex.eu/doc/<document> for the given work URI,
        where <document> is determined by the expression for the work URI for the given
        entity description.
        Note: only retrieves latest doc and only for entities that are in the network.
        
        @param work: the entity description
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
    
    def getLatestExpressionForWork(self, work):
        return self.getExpressionsForWork(work)[-1]
        
    def getExpressionsForWork(self, work):
        # Create sparql query
        query = 'PREFIX mo: <http://www.metalex.eu/schema/1.0#>SELECT DISTINCT * WHERE {?e mo:realizes <' + \
            work + '> }'
            
        # Pass query to sparql endpoint (through regular post request)
        data = urllib2.urlopen('http://doc.metalex.eu:8000/sparql/', 'query=' + query + '&soft-limit=-1')
        
        # Read xml and get results
        xml = mini.parseString(data.read())
        results = xml.getElementsByTagName('result')
#         print 'Number of expressions: ' + str(results.length)
        # If no expressions, return False
        if not results.length:
            return False
        
        # Extract the expression URI's from the results and add each to the
        # list of all expressions for this work
        expressions = []
        for result in results:
            bindings = result.getElementsByTagName('binding')
            expression = bindings[0].getElementsByTagName('uri')[0].firstChild.nodeValue
            expressions.append(expression)
        
        return expressions
    
    def getLatestTitleAndExpressionForBWB(self, bwb):
        """
        Returns a list with the original bwb number, its title and its latest expression
        for /wetten/doc/.
        
        @param bwb: the bwb number (string).
        @return: list of strings: bwb number, title and latest expression. False if no
            expressions have been found.
        """
            
        work = 'http://doc.metalex.eu/id/' + bwb
        expressions = self.getExpressionsForWork(work)
        # If there are no expressions, return False
        if not expressions:
            return False
        
        latestExpression = expressions[-1]
        title = self.getTitleForExpression(latestExpression)
        
        # Convert the metalex expression to /wetten/doc/ expression
        latestExpression = re.sub('^.*eu/id/', '/wetten/doc/', latestExpression) + '/data.xml'
        
        return [bwb, title, latestExpression]
        
    def getTitleForExpression(self, expression):
        """
        Returns title for given expression by querying the sparql endpoint.
        
        @param expression: the expression
        """
        # Create sparql query
        query = 'SELECT DISTINCT ?title WHERE {<' + expression + '>' + \
            '<http://purl.org/dc/terms/title> ?title } LIMIT 1'
#         print 'query: ' + query
        
        # Pass query to sparql endpoint (through regular post request)
        data = urllib2.urlopen('http://doc.metalex.eu:8000/sparql/', 'query=' + query + '&soft-limit=-1')
        
        # Read xml and get result
        xml = mini.parseString(data.read())
        result = xml.getElementsByTagName('result')[0]
        
        # Extract the title from the binding
        binding = result.getElementsByTagName('binding')[0]
        title = binding.getElementsByTagName('literal')[0].firstChild.nodeValue
#         print 'title: ' + title
        return title
    
    def getDocsForIds(self, idExpressions):
        docs = []
        for idExpression in idExpressions:
            docs += [self.getDocForId(idExpression)]
            
        return docs
        
    def getDocForId(self, idExpression):
        """
        Given an expression of the form doc.metalex.eu/id/<expression>,
        returns doc.metalex.eu/doc/<expression>/data.xml
        
        @param idExpression: regular metalex expression URI
        @return: transformed URI, link to xml data for expression
        """
        return re.sub('/id/', '/doc/', idExpression) + '/data.xml'
    
    def getCitedWorkForReference(self, reference):
        """
        Given a reference (both intref and extref), fetches first matching
        work that is cited by the reference.
        
        @param reference: the reference (the "about" value of the inline element)
        @return: the work level URI of the cited source
        """
        # Create the query
        query = 'SELECT ?cited WHERE {\
                 ?e <http://www.w3.org/2002/07/owl#sameAs> <' + reference + '>. \
                 ?e <http://www.metalex.eu/schema/1.0#cites> ?cited } LIMIT 1'
                 
        # Pass query to sparql endpoint (through regular post request)
        data = urllib2.urlopen('http://doc.metalex.eu:8000/sparql/', 'query=' + query + '&soft-limit=-1')
        
        # Read xml and get result
        xml = mini.parseString(data.read())
        result = xml.getElementsByTagName('result')[0]
        
        # Extract the title from the binding
        binding = result.getElementsByTagName('binding')[0]
        citedWork = binding.getElementsByTagName('uri')[0].firstChild.nodeValue
        return citedWork
    
    def getLatestCitedExpressionForReference(self, reference):
        work = self.getCitedWorkForReference(reference)
        return self.getLatestExpressionForWork(work)
    
    def datesForExpressions(self, expressions):
        """
        Given a list of expression URI's, returns a dictionary with two items.
        Item "dates" holds a list of sorted dates (Dutch string format).
        Item "expressions" holds a dictionary with the given expressions and their
        date strings as key.
        
        @param expressions: list of expression URI's.
        @return: dictionary, see above.
        """
        dates = []
        expressionDict = {}
        for expression in expressions:
            dateTuple = self.dateForExpression(expression)
            expressionDict[dateTuple[1]] = expression
            dates += [dateTuple]
            
        # Sort the date tuples by date
        dates.sort(key=lambda x:x[0])
        
        # Only keep the sorted date strings
        sortedDates = [d[1] for d in dates]
        return {'dates':sortedDates, 'expressions':expressionDict}
        
    def dateForExpression(self, expression):
        """
        Returns tuple of date object and date string in Dutch format, e.g. "1 januari 2011",
        for given expression URI.
        
        @param expression: URI containing a date in YYYY-mm-dd format.
        @return: (dateObject, dateString) tuple.
        """
        datePattern = re.compile('\d\d\d\d-\d\d-\d\d')
        match = re.search(datePattern, expression)
        if match:
            dateString = match.group(0)
            exprDate = datetime.datetime.strptime(dateString, '%Y-%m-%d').date()
            dateString = str(exprDate.day) + self.months[exprDate.month] + str(exprDate.year)
            
            return (exprDate, dateString) 
        else:
            return 'Geen datum'
        
    def differingExpressionsForHash(self, hashURI, currentDate):
        """
        Returns a list of expressions that differ from the one defined by the given
        hash. This means the list returned contains the expression for the given hash
        and any other expressions that have not an owl:sameAs relation with the given hash,
        but only one for each hash. The oldest expression for each has (except the current hash)
        is returned.
        
        The algorithm consists of the following queries and steps:
        - Get all expressions that have an owl:sameAs relation with the hash
        - Take the expression with the current date from it
        - Get the work from that expression
        - Get all expressions and their hashes for that work
        - Loop through the sparql results and build a dictionary [hash: (expression, dateTuple)] 
          with |date| being the datetime.date() corresponding to the expression. If the hash isn't
          yet in the dictionary, add the hash and expression. If the hash is already in the
          dictionary, replace the (expression, dateTuple) tuple for that hash if the new date is
          older than the previous date. Also add the key:object pair for the given hash (|hashURI|).
        - Build a dictionary of dateString:expression pairs.
        - Take the date tuples and sort them by date.
        - Make a list with only the date strings (in sorted order).
        - Return a dictionary similar to the one in datesForExpressions().
        This algorithm ensures only a single expression for each available hash is returned,
        that the oldest expression for each hash is used and that the expressions are sorted by date.
        
        @param hashURI: the work URI with a hash at the end.
        @param currentDate: date in YYYY-mm-dd format
        @return: a dictionary with two items:
            Item "dates" holds a list of sorted dates (Dutch string format).
            Item "expressions" holds a dictionary with each expression and its
            date string as key.
        """
        
        # The query to get the expression(s) for the hash.
        query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT DISTINCT ?expression WHERE {
         ?expression owl:sameAs <""" + hashURI + """>
        }
        """
        # Pass query to sparql endpoint (through regular post request)
        data = urllib2.urlopen('http://doc.metalex.eu:8000/sparql/', 'query=' + query + '&soft-limit=-1')
        
        # Read xml and get results
        xml = mini.parseString(data.read())
        results = xml.getElementsByTagName('result')
        
        expressionsForHash = []
        # For each result extract the expression from the binding
        for result in results:
            binding = result.getElementsByTagName('binding')[0]
            expressionsForHash += [binding.getElementsByTagName('uri')[0].firstChild.nodeValue]
        
        currentExpression = ''
        # Find and save the expression for the current date. Then remove it from |expressionsForHash|
        for expression in expressionsForHash:
            if re.search(currentDate, expression):
                currentExpression = expression
                expressionsForHash.remove(expression)
                break
            
        # Get the work level URI for the current expression
        query = """
        PREFIX mo: <http://www.metalex.eu/schema/1.0#>

        SELECT ?work WHERE {
         <""" + currentExpression + """> mo:realizes ?work
        }
        """
        # Pass query to sparql endpoint (through regular post request)
        data = urllib2.urlopen('http://doc.metalex.eu:8000/sparql/', 'query=' + query + '&soft-limit=-1')
        
        # Read xml and get results
        xml = mini.parseString(data.read())
        result = xml.getElementsByTagName('result')[0]
        
        # Get the work URI
        binding = result.getElementsByTagName('binding')[0]
        work = binding.getElementsByTagName('uri')[0].firstChild.nodeValue
        
        # Get all expressions and their hashes for the work
        query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX mo: <http://www.metalex.eu/schema/1.0#>

        SELECT DISTINCT ?expression, ?hash WHERE {
         ?expression mo:realizes <""" + work + """>.
         ?expression owl:sameAs ?hash
        }
        """
        # Pass query to sparql endpoint (through regular post request)
        data = urllib2.urlopen('http://doc.metalex.eu:8000/sparql/', 'query=' + query + '&soft-limit=-1')
        
        # Read xml and get results
        xml = mini.parseString(data.read())
        results = xml.getElementsByTagName('result')
        
        hashesExpressionsAndDates = {}
        # For each result:
        # - If the hash is equal to the given hash, ignore.
        # - Else if the hash isn't yet in the dictionary, add it as key
        #   with the tuple (expression, dateTuple) as object.
        # - Else if the hash is already in the dictionary, replace the object
        #   if the new date is older than the previous date.
        for result in results:
            bindings = result.getElementsByTagName('binding')
            expression = bindings[0].getElementsByTagName('uri')[0].firstChild.nodeValue
            resultHash = bindings[1].getElementsByTagName('uri')[0].firstChild.nodeValue
            
            if resultHash == hashURI:
                continue
            else:
                dateTuple = self.dateForExpression(expression)
                # Convert expression to doc.metalex.eu/doc/.../data.xml format
                docExpression = self.getDocForId(expression)
                
                if resultHash not in hashesExpressionsAndDates:
                    hashesExpressionsAndDates[resultHash] = (docExpression, dateTuple)
                else:
                    previousDate = hashesExpressionsAndDates[resultHash][1][0]
                    if dateTuple[0] < previousDate:
                        hashesExpressionsAndDates[resultHash] = (docExpression, dateTuple)
        
        # Add the current hash and expression and date to the dictionary.
        dateTuple = self.dateForExpression(currentExpression)
        docExpression = self.getDocForId(currentExpression)
        hashesExpressionsAndDates[hashURI] = (docExpression, dateTuple)
        
        # Make dictionary of dateString:expression pairs.
        expressionDict = {hashesExpressionsAndDates[key][1][1]:hashesExpressionsAndDates[key][0] for key in hashesExpressionsAndDates}
        
        # Take the date tuples and sort them
        dateTuples = [hashesExpressionsAndDates[key][1] for key in hashesExpressionsAndDates]
        dateTuples.sort(key=lambda x:x[0])
        
        # Only keep the sorted date strings
        sortedDates = [d[1] for d in dateTuples]
        return {'dates':sortedDates, 'expressions':expressionDict}
        
            
def main():
    sh = SparqlHelper()
    d = sh.differingExpressionsForHash('http://doc.metalex.eu/id/BWBR0011353/hoofdstuk/3/afdeling/3.2/paragraaf/3.2.3/artikel/3.67/al/4c6159e7b11546383a655ce21da3150e1f5ec05a', '2013-01-15')
    print d
    print '\nExecution ended'
    
if __name__ == '__main__':
    main()