'''
Created on 6 mei 2013

Parses SPARQL XML results and converts/stores them to a format
suitable for centrality measurement (networkx graph format).

@author: Ivan
'''

from xml.dom import minidom as mini
import os
import re
import networkx as nx
import time
import pickle

class CitesParser:
    
    def __init__(self, inOrOut='none', makeNetwork=False, logName=False):
        
        # Provide the correct locations for the SPARQL result files.
        self.citesInDir = '/Users/Ivan/Documents/Beta-gamma/KI jaar 2/Afstudeerproject/Project/Cites_in/'
        self.citesOutDir = '/Users/Ivan/Documents/Beta-gamma/KI jaar 2/Afstudeerproject/Project/Cites_out/'
        
        # Get lists of file names.
        self.citeInFiles = self.getCiteFiles(self.citesInDir)
        self.citeOutFiles = self.getCiteFiles(self.citesOutDir)
        
        if(logName):
            self.log = "Starting...\n"
            self.logName = logName + ' '
        else:
            self.logName = False
            
        # Assume all citations will be parsed succesfully
        self.encounteredUnknownPattern = False
        
        self.makeNetwork = makeNetwork
        if(makeNetwork):
            self.G = nx.Graph()
        
        # Parse the citations for incoming or outgoing or both or none
        if inOrOut == 'both':
            self.parseCitations('out')
            self.parseCitations('in')
        elif inOrOut == 'in' or inOrOut == 'out':
            self.parseCitations(inOrOut)
        
        # Write the log to disk if logging is enabled    
        if(logName):
            self.writeLog()
        
        # Save network to disk if a network was made    
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
        @return: list of file names
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
        
        # Parse each file    
        for bwbFile in files:
            print '\nParsing file: ' + bwbFile + '...'
            
            # Get xml tree for the current file
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
            
            # Handle all results for the current file
            for result in results:
                bindings = result.getElementsByTagName('binding')
                self.handleBindings(bindings, inOrOut)
   
    def getEncounteredUnknownPattern(self):
        return self.encounteredUnknownPattern
    
    def handleBindings(self, bindings, inOrOut):
        '''
        Extracts the correct URI's from the bindings and
        retrieves shorter descriptions to use as labels in the
        network.
        @param bindings: list of xml bindings
        @param inOrOut: 'in' or 'out' to discriminate between
            the structure of the bindings of incoming and outgoing
            citations 
        '''
        # Get uri's for citing and cited entities
        if inOrOut == 'out':
            # For outgoing citations, the desired URI's are the second and third variables.
            # Note: if SPARQL results change in format (more variables, different order),
            #    the |bindings| indices must be changed accordingly
            citing = bindings[1].getElementsByTagName('uri')[0].firstChild.nodeValue
            cited = bindings[2].getElementsByTagName('uri')[0].firstChild.nodeValue
        else:
            # For incoming citations, the desired URI's are the first and second variables.
            # Note: see previous note.
            citing = bindings[0].getElementsByTagName('uri')[0].firstChild.nodeValue
            cited = bindings[1].getElementsByTagName('uri')[0].firstChild.nodeValue
        
        if(self.logName):
            self.log += '\n\nCiting unit: ' + citing
            self.log += '\nCited unit: ' + cited
            
        # Get entity description for citing element and for cited one
        citingEntity = self.entityDescription(citing)
        citedEntity = self.entityDescription(cited)
        
        # If a network should be created and both URI's were parsed successfully,
        # add an edge.
        # Note: parallel edges aren't allowed, so if an edge already exists, it
        # isn't added again.
        if(self.makeNetwork and citingEntity and citedEntity):
            # Get work level URI's
            citingWork = self.workLevelURI(citing, citingEntity)
            citedWork = self.workLevelURI(cited, citedEntity)
            
            # Add nodes with work level as attribute "work"
            self.G.add_node(citingEntity, work=citingWork)
            self.G.add_node(citedEntity, work=citedWork)
            
            # Add the edge
            self.G.add_edge(citingEntity, citedEntity)    
    
    def workLevelURI(self, uri, entityDescription):
        """
        Given a entityDescription, a shorter work-level URI is returned
        
        @param entityDescription: the entityDescription
        @param uri: the original full expression URI
        @return: string with higher level work URI
        """
        # First get last two parts of entity
        # Original entity, i.e. entity description without bwb might consist of
        # more than two parts (like "hoofdstuk/kop/2"), but since we are matching
        # against the original URI, the last two parts are enough to get everything
        # except the part after the entity (containing uninteresting elements like
        # al, li, etc.).
        entity = re.findall('/[\w|\.|:]+/[\w|\.|:]+$', entityDescription)
        # If there is a match, take first object
        if entity:
            entity = entity[0]
        # Else we are dealing with a BWB only
        else:
            entity = ''
        
        # Take everything from original expression URI, except parts after entity description
        workURI = re.findall('^.*' + entity, uri)
        return workURI
    
    def entityDescription(self, citation):
        """
        Given a URI, creates and returns a shorter description of the entity,
        ready for use as node name for the network.
        
        @param citation: the citation URI (string)
        @return: the new, shorter description (string), or False if parsing
            wasn't successful.
        """
        
        # First, retrieve the BWB number
        BWB = re.findall('BWBR\d{7}', citation)
        if BWB.__len__() > 0:
            # If the BWB was found, take it
            BWB = BWB[0]
        elif re.findall('BWBW\d{5}', citation).__len__() > 0:
            # Else if the citing/cited entity has a BWBW\d{5} pattern,
            # retrieve that one
            BWB = re.findall('BWBW\d{5}', citation)[0]    
        else:
            # Unknown BWB pattern
            print '\nCritical: cited has no BWB:\n' + citation
            return False
          
        entity = False
        # Find the first match and handle accordingly.
        # The order is very important, putting a higher level
        # (e.g. hoofdstuk) before a lower level entity (e.g. artikel)
        # will result in many lower level entities being wrongly
        # abstracted to the higher level.
        if re.search('BWBR\d{7}$', citation):
            # If the cited entity is an entire BWB, then the entity
            # is empty.
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
            # Return BWB/entity and replace possible occurrences of %3A with ':'
            return re.sub('%3A', ':', BWB + entity)
            
        else:
            # The citation pattern wasn't recognized.
            # Return False and set |encounteredUnknownPattern| to True.
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
        
        # If there is a 'kop' in the URI, add it to the 'hoofdstuk'
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
        """
        A bijlage can contain 'artikel' or 'kop' instances. If so,
        these are to be added to '/bijlage/'
        """
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
        # First try to match a 'circulaire-tekst' pattern, return it
        # if it exists.
        circulaire = re.findall('/circulaire/[\w|\.]+/circulaire-tekst/[\w|\.]+', ref)
        if len(circulaire) > 0:
            return circulaire[0]
        
        # Else match a standard 'circulaire' pattern.
        circulaire = re.findall('/circulaire/[\w|\.]+', ref)
        if len(circulaire) > 0:
            return circulaire[0]
        else:
            return False
    
    def handleRegeling(self, ref):
        # First try to match a 'regeling-tekst' pattern, return it
        # if it exists.
        regeling = re.findall('/regeling/[\w|\.]+/regeling-tekst/[\w|\.]+', ref)
        if len(regeling) > 0:
            return regeling[0]
        
        # Else match a regular 'regeling' pattern.
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