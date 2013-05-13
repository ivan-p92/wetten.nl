'''
Created on 6 mei 2013

Parses SPARQL XML results and converts/stores them to a format
suitable for centrality measurement.

@author: Ivan
'''

from xml.dom import minidom as mini
import os
import re
import networkx as nx
import time
import pickle

class CitesParser:
    
    def __init__(self, inOrOut='both', makeNetwork=False, logName=False):
        
        # Provide the correct locations for the SPARQL result files
        self.citesInDir = '../../Cites_in/'
        self.citesOutDir = '../../Cites_out/'
        
        self.citeInFiles = self.getCiteFiles(self.citesInDir)
        self.citeOutFiles = self.getCiteFiles(self.citesOutDir)
        
        if(logName):
            self.log = "Starting...\n"
            self.logName = logName + ' '
        else:
            self.logName = False
        self.encounteredUnknownPattern = False
        
        self.makeNetwork = makeNetwork
        if(makeNetwork):
            self.G = nx.Graph()
        
        # Parse the citations for incoming or outgoing
        if inOrOut == 'both':
            self.parseCitations('out')
            self.parseCitations('in')
        elif inOrOut == 'in' or inOrOut == 'out':
            self.parseCitations(inOrOut)
            
        if(logName):
            self.writeLog()
            
        if(makeNetwork):
            fileName = 'Graph ' + time.ctime(time.time())
            nx.write_gml(self.G, fileName + '.gml')
            pickle.dump(self.G, open(fileName + '.pickle', 'w'))
            print '\nDumped graph at: "' + fileName + '", (.pickle and .gml)'
    
    def getCiteFiles(self, dirPath):
        '''
        Retrieves all file names for xml files that start with BWB at
        given path.
        
        @param dirPath: path of directory (relative or absolute) 
        '''
        
        files = []
        for cites in os.listdir(dirPath):
            if cites.startswith('BWB') and cites.endswith('.xml'):
                files.append(cites)
        
        print files     
        return files
    
    def writeLog(self):
        fileName = self.logName + time.ctime(time.time()) + ".txt"
        logFile = open(fileName, 'w')
        logFile.write(self.log)
        logFile.close()
        print "\nLog written to file: '" + fileName + "'"
     
    def parseCitations(self, inOrOut):
        '''
        Parses the citations in the files
        @param inOrOut: string determining incoming ('in') or outgoing ('out')
            citations
        '''
        
        files = None
        citesDir = None
        if inOrOut == 'out':
            print '\nParsing all outgoing citations...'
            if(self.logName):
                self.log += ('\n/------------------------------/' +
                             '\n/----- Outgoing citations -----/' +
                             '\n/------------------------------/')
            files = self.citeOutFiles
            citesDir = self.citesOutDir
        elif inOrOut == 'in':
            print '\nParsing all incoming citations...'
            if(self.logName):
                self.log += ('\n/------------------------------/' +
                             '\n/----- Incoming citations -----/' +
                             '\n/------------------------------/')
            files = self.citeInFiles
            citesDir = self.citesInDir
        else:
            return
            
        for bwbFile in files:
            print '\nParsing file: ' + bwbFile + '...'
            xml = mini.parse(citesDir + bwbFile)
#             variables = xml.getElementsByTagName('variable')
#             print 'Variables: '
#             for var in variables:
#                 print var.attributes['name'].value
                
            results = xml.getElementsByTagName('result')
            print 'Number of SPARQL results: ' + str(results.length)
            
            if(self.logName):
                self.log += '\n##################\nParsing file: ' + bwbFile + '...'
                self.log += '\nNumber of SPARQL results: ' + str(results.length)
                self.log += '\n##################'
            print 'Handling results...'
            
            for result in results:
                bindings = result.getElementsByTagName('binding')
                self.handleBindings(bindings, inOrOut)
   
    def getEncounteredUnknownPattern(self):
        return self.encounteredUnknownPattern
    
    def handleBindings(self, bindings, inOrOut):
        '''
        
        '''
        # Get uri's for citing and cited entities
        if inOrOut == 'out':   
            citing = bindings[1].getElementsByTagName('uri')[0].firstChild.nodeValue
            cited = bindings[2].getElementsByTagName('uri')[0].firstChild.nodeValue
        else:
            citing = bindings[0].getElementsByTagName('uri')[0].firstChild.nodeValue
            cited = bindings[1].getElementsByTagName('uri')[0].firstChild.nodeValue
        
        if(self.logName):
            self.log += '\n\nCiting unit: ' + citing
            self.log += '\nCited unit: ' + cited
            
        # Get entity description for citing element and for cited one
        citingEntity = self.entityDescription(citing)
        citedEntity = self.entityDescription(cited)
        
        if(self.makeNetwork and citingEntity and citedEntity):
            self.G.add_edge(citingEntity, citedEntity)    

    def entityDescription(self, citation):
        BWB = re.findall('BWBR\d{7}', citation)
        if BWB.__len__() > 0:
            BWB = BWB[0]
        elif re.findall('BWBW\d{5}', citation).__len__() > 0:
            BWB = re.findall('BWBW\d{5}', citation)[0]    
        else:
            return False
            print '\nCritical: cited has no BWB:\n' + citation
          
        entity = False  
        if re.search('BWBR\d{7}$', citation):
            entity = ''    
        if citation.find('/bijlage/') > -1:
            entity = self.handleBijlage(citation)
        elif citation.find('/titeldeel/') > -1:
            entity = self.handleTiteldeel(citation)
        elif citation.find('/considerans/') > -1:
            entity = self.handleConsiderans(citation)
        elif citation.find('/artikel/') > -1:
            entity = self.handleArtikel(citation)
        elif citation.find('/hoofdstuk/') > -1:
            entity = self.handleHoofdstuk(citation)
        elif citation.find('/circulaire.divisie/') > -1:
            entity = self.handleCirculaireDivisie(citation)
        elif citation.find('/circulaire/') > -1:
            entity = self.handleCirculaire(citation)
        elif citation.find('/regeling/') > -1:
            entity = self.handleRegeling(citation)
        elif citation.find('/paragraaf/') > -1:
            entity = self.handleParagraaf(citation)
        elif citation.find('/afdeling/') > -1:
            entity = self.handleAfdeling(citation)
        elif citation.find('/deel/') > -1:
            entity = self.handleDeel(citation)
        elif citation.find('/wijzig-artikel/') > -1:
            entity = self.handleWijzigArtikel(citation)
            
        if BWB and (entity or entity == ''):
            if(self.logName):
                self.log += '\nCited BWB/entity: ' + BWB + entity
            return BWB + entity
            
        else:
            self.encounteredUnknownPattern = True
            print 'Unknown cited pattern: ' + citation
            if(self.logName):
                self.log += '\nUnknown cited pattern'
                
            return False

    def handleArtikel(self, ref):
        artikel = ref.split('artikel/')[1].split('/')[0]
        
        return '/artikel/' + artikel
    
    def handleConsiderans(self, ref):
        considerans = ref.split('considerans/')[1].split('/')[0]
        
        return '/considerans/' + considerans
    
    def handleHoofdstuk(self, ref):
        hoofdstuk = ref.split('hoofdstuk/')[1].split('/')[0]
        
        if ref.find('/kop/') > -1:
            kop = self.handleKop(ref)
            return '/hoofdstuk/' + hoofdstuk + kop
        else:
            return '/hoofdstuk/' + hoofdstuk
    
    def handleKop(self, ref):
        try:
            kop = ref.split('/kop/')[1].split('/')[0]
        except IndexError:
            print 'Kop index error for ref: ' + ref
            return False
            
        return '/kop/' + kop
        
    def handleBijlage(self, ref):
        bijlage = ref.split('bijlage/')[1].split('/')[0]
        
        if ref.find('artikel') > -1:
            artikel = self.handleArtikel(ref)
            return '/bijlage/' + bijlage + artikel
        elif ref.find('/kop/') > -1:
            kop = self.handleKop(ref)
            return '/bijlage/' + bijlage + kop
        else:
            return '/bijlage/' + bijlage
        
    def handleTiteldeel(self, ref):
        titeldeel = ref.split('titeldeel/')[1].split('/')[0]
        
        return '/titeldeel/' + titeldeel
    
    def handleAfdeling(self, ref):
        afdeling = ref.split('afdeling/')[1].split('/')[0]
        
        return '/afdeling/' + afdeling
    
    def handleParagraaf(self, ref):
        paragraaf = ref.split('paragraaf/')[1].split('/')[0]
        
        return '/paragraaf/' + paragraaf
    
    def handleCirculaireDivisie(self, ref):
        circDiv = ref.split('circulaire.divisie/')[-1].split('/')[0]
        return '/circulaire.divisie/' + circDiv
    
    def handleCirculaire(self, ref):
        circulaire = re.findall('/circulaire/[\w|\.]+/circulaire-tekst/[\w|\.]+', ref)
        if len(circulaire) > 0:
            return circulaire[0]
        
        circulaire = re.findall('/circulaire/[\w|\.]+', ref)
        if len(circulaire) > 0:
            return circulaire[0]
        else:
            return False
    
    def handleRegeling(self, ref):
        regeling = re.findall('/regeling/[\w|\.]+/regeling-tekst/[\w|\.]+', ref)
        if len(regeling) > 0:
            return regeling[0]
        
        regeling = re.findall('/regeling/[\w|\.]+', ref)
        if len(regeling) > 0:
            return regeling[0]
        else:
            return False
    
    def handleDeel(self, ref):
        deel = re.findall('/deel/[\w|\.]+', ref)
        if len(deel) > 0:
            return deel[0]
        else:
            return False
        
    def handleWijzigArtikel(self, ref):
        wa = ref.split('wijzig-artikel/')[1].split('/')[0]
        return '/wijzig-artikel/' + wa
    
def main():
    print 'Starting...'
    
#     G=nx.Graph()
#     G.add_edges_from([(1,2),(1,3)])
#     G.add_node("spam") 
#     
#     nx.draw(G)
#     plt.show()

    start_time = time.time()
    citesParser = CitesParser(inOrOut = 'both', makeNetwork = True)
    end_time = time.time() - start_time
    
    if(citesParser.getEncounteredUnknownPattern()):
        print "\nWatch out: unknown pattern found, check log file!"
    else:
        print"\nAll citations handled successfully!"
    print "\nDone! Elapsed time: " + str(int(end_time)) + " seconds"

if __name__ == '__main__':
    main()