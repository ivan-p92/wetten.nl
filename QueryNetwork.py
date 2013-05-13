'''
Created on 9 mei 2013

The purpose of this module is to use the graph representation of the citation network
to perform various analyses, mostly using the networkx package.

@author: Ivan
'''

# from xml.dom import minidom as mini
# import os
# import re
import networkx as nx
import time
import pickle
import re

class QueryNetwork:
    
    def __init__(self, graphPath='graph.pickle'):
        t = time.time()
        print 'Loading graph from file: "' + graphPath + '"...'
        self.G = pickle.load(open(graphPath, 'r'))
        print 'Graph loading time: ' + str(int(time.time() - t)) + ' seconds'
        
        self.degree = None
        self.degreeCentrality = None
        self.betweenness = None
        self.eigenvector = None
        self.loadCentrality = None
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
        self.degree = nx.degree(self.G)
        print 'Degree calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.degree, open('degree.pickle', 'w'))
        
    def calcAndPickleDegreeCentrality(self):
        """
        Calculates the degree centrality for all nodes in the network and
        saves the resulting dictionary to the hard drive.
        """
        t = time.time()
        self.degreeCentrality = nx.degree_centrality(self.G)
        print 'Degree centrality calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.degreeCentrality, open('degree_centrality.pickle', 'w'))
        
    def calcAndPickleBetweenness(self):
        """
        Calculates the betweenness centrality for all nodes in the network and
        saves the resulting dictionary to the hard drive.
        """
        t = time.time()
        self.betweenness = nx.betweenness_centrality(self.G)
        print 'Betweenness centrality calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.betweenness, open('betweenness_centrality.pickle', 'w'))
        
    def calcAndPickleEigenvector(self):
        """
        Calculates the eigenvector centrality for all nodes in the network and
        saves the resulting dictionary to the hard drive.
        Note: doesn't converge, so doesn't yield a result
        """
        t = time.time()
        self.eigenvector = nx.eigenvector_centrality(self.G, max_iter=1000)
        print 'Eigenvector centrality calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.eigenvector, open('eigenvector_centrality.pickle', 'w'))
        
    def calcAndPickleLoadCentrality(self):
        """
        Calculates the load centrality for all nodes in the network and
        saves the resulting dictionary to the hard drive.
        Note: very similar to betweenness centrality
        """
        t = time.time()
        self.loadCentrality = nx.load_centrality(self.G)
        print 'Load centrality calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.loadCentrality, open('load_centrality.pickle', 'w'))
    
    def loadMeasurements(self):
        """
        Loads (most) performed measurements from disk into memory. These are all
        dictionaries.
        Note: doesn't perform existence check, will terminate if files don't exist
        """
        t = time.time()
        self.degree = pickle.load(open('degree.pickle', 'r'))
        self.degreeCentrality = pickle.load(open('degree_centrality.pickle', 'r'))
        self.betweenness = pickle.load(open('betweenness_centrality.pickle', 'r'))
#         self.eigenvector = None
        self.loadCentrality = pickle.load(open('load_centrality.pickle', 'r'))
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
        Simply returns neigbours for given node (entity)
        @param entity: the node
        @return: list of nodes
        """
        return self.G.neighbors(entity)
    
    def getRelatedEntities(self, entity):
        """
        Retrieves all entities (nodes) related to the given one.
        Related entities are either direct neighbours or neighbours
        of those neighbours.
        @param entity: the entity, e.g. "BWBR0011353/artikel/5.3"
        @return: set of nodes, in list format 
        """
        directNeighbours = self.getNeighboursForEntity(entity)
        
        if not directNeighbours:
            return False
        
        indirectNeighbours = []
        # Add indirect neighbours to the direct ones
        for neighbour in directNeighbours:
            indirectNeighbours += self.getNeighboursForEntity(neighbour)
            
        return list(set(directNeighbours + indirectNeighbours))
    
    def sortRelatedEntities(self, entity):
        """
        Retrieves and sorts related entities.
        @param entity: entity for which related entities will be taken
        """
        relatedEntities = self.getRelatedEntities(entity)
        if not relatedEntities:
            return []
        
        return self.sortEntities(relatedEntities)
    
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
        print '\nDegree centralities:\n' + str(degreeCentrality)
        print '\n\nBetweenness centralities:\n' + str(betweenness)
        
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
        
        # Conversion to dictionaries solely for debugging purposes (analysing
        # ranking and original degree/betweenness values).
        degreeCentrality = dict(degreeCentrality)
        betweenness = dict(betweenness)
        for entity in sortedEntities:
            print entity[0] + ', \t\t' + str(degreeCentrality[entity[0]]) + ', \t' + str(betweenness[entity[0]])
        
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

def main():
    
    queryNetwork = QueryNetwork('graph.pickle')
    
    while True:
        node = raw_input('\nGive node name or type "stop" to quit: ')
        if node == 'stop':
            break
        
        start_time = time.time()
        print 'Query result: ' + str(queryNetwork.getDegree(node))
        print 'Query time: ' + str(int(time.time() - start_time)) + ' seconds'
    pass
    
    print '\nExecution ended'
if __name__ == '__main__':
    main()