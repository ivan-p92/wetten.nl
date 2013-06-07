'''
Created on 9 mei 2013

The purpose of this module is to use the graph representation of the citation network
to perform various analyses, mostly using the networkx package.

@author: Ivan
'''

# from xml.dom import minidom as mini
# import os
# import re
from xml.dom import minidom as mini
import urllib2
import networkx as nx
import time
import pickle
import re
from os import path

class QueryNetwork:
    
    def __init__(self, graphFileName='graph.pickle'):
        """
        Note: graph file must be in same directory as this module.
        """
        self.dirName = path.dirname(__file__)
        t = time.time()
        print 'Loading graph from file: "' + self.dirName + '/' + graphFileName + '"...'
        self.G = pickle.load(open(self.dirName + '/' + graphFileName, 'r'))
        print 'Graph loading time: ' + str(int(time.time() - t)) + ' seconds'

        self.degree = None
        self.inDegree = None
        self.degreeCentrality = None
        self.betweenness = None
        self.eigenvector = None
        self.loadCentrality = None
        self.closenessCentrality = None
        self.didLoadMeasurements = False
        
    def getDegreeForNode(self, node):
        """
        Returns the degree (in + out) for given node.
        @param node: string label of node.
        @return: the degree (integer)
        """
        if not self.didLoadMeasurements:
            self.loadMeasurements()
            
        return self.degree[node]
    
    def calcAndPickleDegree(self):
        """
        Calculates the degree (in + out) for all nodes in the network and
        saves the resulting dictionary to the hard drive.
        """
        t = time.time()
        print '\nCalculating degree...'
        self.degree = nx.degree(self.G)
        print 'Degree calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.degree, open(self.dirName + '/degree.pickle', 'w'))
        
    def calcAndPickleInDegree(self):
        """
        Calculates in-degree for all nodes in the network and saves the
        resulting dictionary.
        """
        t = time.time()
        print '\nCalculating in-degree...'
        self.inDegree = self.G.in_degree(self.G.nodes())
        print 'Degree centrality calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.inDegree, open(self.dirName + '/in_degree.pickle', 'w'))
        
    def calcAndPickleDegreeCentrality(self):
        """
        Calculates the degree centrality for all nodes in the network and
        saves the resulting dictionary to the hard drive.
        """
        t = time.time()
        print '\nCalculating degree centrality...'
        self.degreeCentrality = nx.degree_centrality(self.G)
        print 'Degree centrality calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.degreeCentrality, open(self.dirName + '/degree_centrality.pickle', 'w'))
        
    def calcAndPickleBetweenness(self):
        """
        Calculates the betweenness centrality for all nodes in the network and
        saves the resulting dictionary to the hard drive.
        """
        # Convert the DiGraph to normal graph
        G = self.G.to_undirected()
        t = time.time()
        print '\nCalculating betweenness centrality...'
        self.betweenness = nx.betweenness_centrality(G)
        print 'Betweenness centrality calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.betweenness, open(self.dirName + '/betweenness_centrality.pickle', 'w'))
        
    def calcAndPickleEigenvector(self):
        """
        Calculates the eigenvector centrality for all nodes in the network and
        saves the resulting dictionary to the hard drive.
        Note: doesn't converge, so doesn't yield a result
        """
        t = time.time()
        print '\nCalculating eigenvector centrality...'
        self.eigenvector = nx.eigenvector_centrality(self.G)
        print 'Eigenvector centrality calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.eigenvector, open(self.dirName + '/eigenvector_centrality.pickle', 'w'))
        
    def calcAndPickleLoadCentrality(self):
        """
        Calculates the load centrality for all nodes in the network and
        saves the resulting dictionary to the hard drive.
        Note: very similar to betweenness centrality
        """
        # Convert the DiGraph to normal graph
        G = self.G.to_undirected()
        t = time.time()
        print '\nCalculating load centrality...'
        self.loadCentrality = nx.load_centrality(G)
        print 'Load centrality calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.loadCentrality, open(self.dirName + '/load_centrality.pickle', 'w'))
        
    def calcAndPickleClosenessCentrality(self):
        """
        Calculates the closeness centrality for all nodes in the network and
        saves the resulting dictionary to the hard drive.
        """
        # Convert the DiGraph to normal graph
        G = self.G.to_undirected()
        t = time.time()
        print '\nCalculating closeness centrality...'
        self.closenessCentrality = nx.closeness_centrality(G)
        print 'Closeness centrality calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.closenessCentrality, open(self.dirName + '/closeness_centrality.pickle', 'w'))
    
    def calcAndPickleAll(self):
#         self.calcAndPickleDegree()
        self.calcAndPickleInDegree()
        self.calcAndPickleDegreeCentrality()
        self.calcAndPickleBetweenness()
#         self.calcAndPickleClosenessCentrality()
#         self.calcAndPickleLoadCentrality()
#         self.calcAndPickleEigenvector()
        print '\nCalculated and pickled all..'
    
    def loadMeasurements(self):
        """
        Loads (most) performed measurements from disk into memory. These are all
        dictionaries.
        Note: doesn't perform existence check, will terminate if files don't exist
        """
        t = time.time()
#         self.degree = pickle.load(open(self.dirName + '/degree.pickle', 'r'))
        self.inDegree = pickle.load(open(self.dirName + '/in_degree.pickle', 'r'))
        self.degreeCentrality = pickle.load(open(self.dirName + '/degree_centrality.pickle', 'r'))
        self.betweenness = pickle.load(open(self.dirName + '/betweenness_centrality.pickle', 'r'))
#         self.eigenvector = None
#         self.loadCentrality = pickle.load(open(self.dirName + '/load_centrality.pickle', 'r'))
#         self.closenessCentrality = pickle.load(open(self.dirName + '/closeness_centrality.pickle', 'r'))
        print 'Loaded measurements in ' + str(int(time.time() - t)) + ' seconds'
        self.didLoadMeasurements = True
        
    def getNodesForBWB(self, bwb):
        """
        Given a BWB number, all nodes in the network that belong to the source
        specified by the BWB number are retrieved.
        @param bwb: the BWB code (e.g. BWBR0011353)
        @return: list of nodes
        """
        r = re.compile(bwb + '/.*')
        nodes = filter(r.match, self.G.nodes())
        return nodes
    
    def getNeighboursForEntity(self, entity):
        """
        Returns neigbours for given node (entity), set of predecessors + successors
        @param entity: the node
        @return: list of nodes
        """
        predecessors = self.G.predecessors(entity)
        successors = self.G.successors(entity)
        return list(set(predecessors + successors))
    
    def getRelatedEntities(self, entity):
        """
        Retrieves all entities (nodes) related to the given one.
        Related entities are either direct neighbours or neighbours
        of those neighbours.
        @param entity: the entity, e.g. "BWBR0011353/artikel/5.3"
        @return: list of two lists: first the direct neighbours,
            then the indirect ones. 
        """
        directNeighbours = self.getNeighboursForEntity(entity)
        
        if not directNeighbours:
            return False
        
        """
        # Use this to also look for indirect neighbours
        indirectNeighbours = []
        # Add indirect neighbours to the direct ones
        for neighbour in directNeighbours:
            indirectNeighbours += self.getNeighboursForEntity(neighbour)
        
        indirectNeighbours = list(set(indirectNeighbours))    
        return [directNeighbours] + [indirectNeighbours]"""
        return [directNeighbours]
    
    def sortRelatedEntities(self, entity):
        """
        Retrieves and sorts related entities. Separates entities from the
        same BWB and those from other BWB's
        @param entity: entity for which related entities will be taken
        """
        bwb = entity.split('/')[0]
        relatedEntities = self.getRelatedEntities(entity)
        if not relatedEntities:
            return []
        
        sortedDirect = self.sortEntities(relatedEntities[0])
        
        """
        # Use this if indirect neighbours must be used
        if relatedEntities[1]:
            sortedIndirect = self.sortEntities(relatedEntities[1])
        else:
            sortedIndirect = []
        
        allEntities = sortedDirect + sortedIndirect
        """
        
        allEntities = sortedDirect
        return self.separateInternalFromExternal(allEntities, bwb)
    
    def separateInternalFromExternal(self, entities, bwb):
        """
        Given a list of entities and a BWB number, the internal entities
        are separated from the external ones. Internal entities are entities
        that belong to the given BWB.
        
        @param entities: list of entity descriptions.
        @param bwb: the BWB number to use for the separation.
        @return: a dictionary with two lists, one for the internal and one
            for the external entities.
        """
        internal = []
        external = []
        for entity in entities:
            if entity.startswith(bwb):
                internal += [entity]
            else:
                external += [entity]
        
        return {'internal': internal, 'external': external}
    
    def sortEntitiesForBWB(self, bwb):
        """
        Retrieves all entities for the given BWB code and sorts them.
        """
        nodes = self.getNodesForBWB(bwb)
        if not nodes:
            return []
        
        return self.sortEntities(nodes)
    
    def sortEntities(self, entities):
        """
        Returns a list of the given entities, sorted by combining
        degree centrality and betweenness centrality. This combination
        is done by first sorting the nodes by degree centrality and betweenness centrality
        separately and then taking the sum of the indices of the nodes as the new ranking.
        This means that an entity (e.g. "BWBR0011353/artikel/5.3") with the second highest
        degree centrality and the sixth highest betweenness centrality gets a ranking of 8,
        which is then less than an entity that is fourth on degree centrality but second
        on betweenness.
        """    
        if not self.didLoadMeasurements:
            self.loadMeasurements()
        
        # Retrieve sorted lists of tuples for degree and betweenness centrality    
        degreeCentrality = self.orderNodesByDegreeCentrality(entities)
        betweenness = self.orderNodesByBetweenness(entities)
        
#         closeness = self.orderNodesByCloseness(entities)
        #print '\nDegree centralities:\n' + str(degreeCentrality)
        #print '\n\nBetweenness centralities:\n' + str(betweenness)
        
        degreeIndices = {}
        betweennessIndices = {}
        # Associate each entity with its index (ranking) in both degree and
        # betweenness centrality.
        for i in range(len(degreeCentrality)):
            degreeIndices[degreeCentrality[i][0]] = i
        for i in range(len(betweenness)):
            betweennessIndices[betweenness[i][0]] = i
        
        # Create a list of tuples of the form: 
        # [(entity, degreeCentralityRanking, BetweennessCentralityRanking)]    
        mergedIndices = [(k, degreeIndices[k], betweennessIndices[k]) for k in degreeIndices.keys()]
        
        # Sort the list by taking the sum of the rankings
        sortedEntities = sorted(mergedIndices, key = lambda x: x[1] + x[2])
        
        # Conversion to dictionaries solely for debugging purposes (analyzing
        # ranking and original degree/betweenness values).
        degreeCentrality = dict(degreeCentrality)
        betweenness = dict(betweenness)
#         closeness = dict(closeness)
        for entity in sortedEntities:
            print entity[0] + ', \t\t' + str(degreeCentrality[entity[0]]) + ', \t' + str(betweenness[entity[0]])
#                 + ', \t' + str(closeness[entity[0]])
        print '\n\n'
        
        # Return a list of only the entities
        return [entity[0] for entity in sortedEntities]
    
    def orderNodesByDegree(self, nodes):
        """
        Returns a list of the nodes and their degrees, sorted by degree.
        @param nodes: list of nodes.
        @return: list of tuples in the form of [(node, degree)]
        """
        # Get the degree values for given nodes
        degree = [(k, self.degree[k]) for k in nodes]
        
        # Sort them from large to small
        degree.sort(key= lambda x: x[1], reverse=True)
        return degree
    
    def orderNodesByDegreeCentrality(self, nodes):
        """
        Returns a list of the nodes and their degree centrality values,
        sorted by degree centrality.
        @param nodes: list of nodes.
        @return: list of tuples in the form of [(node, degreeCentrality)]
        """
        # Get the degree centrality values for given nodes
        result = [(k, self.degreeCentrality[k]) for k in nodes]
        
        # Sort them from large to small
        result.sort(key= lambda x: x[1], reverse=True)
        return result
    
    def orderNodesByBetweenness(self, nodes):
        """
        Returns a list of the nodes and their betweenness centrality values,
        sorted by betweenness centrality.
        @param nodes: list of nodes.
        @return: list of tuples in the form of [(node, betweennessCentrality)]
        """
        # Get the betweenness values for given nodes
        result = [(k, self.betweenness[k]) for k in nodes]
        
        # Sort them from large to small
        result.sort(key= lambda x: x[1], reverse=True)
        return result
    
    def orderNodesByCloseness(self, nodes):
        """
        Returns a list of the nodes and their closeness centrality values,
        sorted by closeness centrality.
        @param nodes: list of nodes.
        @return: list of tuples in the form of [(node, closenessCentrality)]
        """
        # Get the betweenness values for given nodes
        result = [(k, self.closenessCentrality[k]) for k in nodes]
        
        # Sort them from large to small
        result.sort(key= lambda x: x[1], reverse=True)
        return result
    
    def entityIsInGraph(self, node):
        """
        Returns True if the node is in the graph and otherwise False.
        @param node: entity description for node.
        @return: True or False
        """
        return self.G.has_node(node)
        
def main():
    
    queryNetwork = QueryNetwork('graph.pickle')
    
    while True:
        node = raw_input('\nGive node name or type "stop" to quit: ')
        if node == 'stop':
            break
        
        start_time = time.time()
        print 'Query result: ' + str(queryNetwork.sortRelatedEntities(node))
        print 'Query time: ' + str(int(time.time() - start_time)) + ' seconds'
    pass
    
    print '\nExecution ended'
if __name__ == '__main__':
    main()