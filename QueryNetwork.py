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
        
        neighbours = list(set(predecessors + successors))
        
        return neighbours
    
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
    
    def sortRelatedEntities(self, entity, maxResults = 0):
        """
        Retrieves and sorts related entities. Separates entities from the
        same BWB and those from other BWB's.
        
        @param entity: entity for which related entities will be taken.
        @param maxResults: maximum number of sorted entities to return.
            If all entities are required, provide 0 (default).
        @return: dictionary with the sorted entities returned by self.sortEntities.
        """
        bwb = entity.split('/')[0]
        relatedEntities = self.getNeighboursForEntity(entity)
        if not relatedEntities:
            return []
        
        # Sort entities.
        sortedEntities = self.sortEntities(relatedEntities, maxResults, separate = True, bwb = bwb)
        
        return sortedEntities
    
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
    
    def sortEntitiesForBWB(self, bwb, maxResults = 0):
        """
        Retrieves all entities for the given BWB code and sorts them.
        
        @param bwb: BWB code.
        @param maxResults: maximum number of sorted entities to return.
            If all entities are required, provide 0 (default).
        """
        nodes = self.getNodesForBWB(bwb)
        if not nodes:
            return []
        
        return self.sortEntities(nodes, maxResults)
    
    def sortEntities(self, entities, maxResults = 0, separate = False, bwb = None):
        """
        Returns a dictionary of lists with each list consisting of the
        given entities, sorted by different methods. The three methods used
        are in-degree, degree centrality and betweenness centrality. The
        maximum final number of returned entities for each method is determined
        by maxResults.
        
        @param entities: list of entities to sort.
        @param maxResults: maximum number of sorted entities to return.
            If all entities are required, provide 0 (default).
        @param separate: whether to separate internal from external sources. If desired,
            provide bwb code.
        @param bwb: bwb code to separate internal from external sources. Only required
            if separation is required.
        @return: dictionary with list of sorted entities for each method, with the
            method name as key.
        """
        if not self.didLoadMeasurements:
            self.loadMeasurements()
        
        # Retrieve sorted lists of tuples for the three methods 
        inDegree = self.orderNodesByInDegree(entities)
        degreeCentrality = self.orderNodesByDegreeCentrality(entities)
        betweenness = self.orderNodesByBetweenness(entities)
        
        # Only keep number of desired results, but take separation into account
        if separate:
            separatedInDegree = self.separateInternalFromExternal(inDegree, bwb)
            inDegree = {}
            if maxResults:
                inDegree['internal'] = separatedInDegree['internal'][0:maxResults]
                inDegree['external'] = separatedInDegree['external'][0:maxResults]
            else:
                inDegree['internal'] = separatedInDegree['internal']
                inDegree['external'] = separatedInDegree['external']
                
            separatedDegreeCentrality = self.separateInternalFromExternal(degreeCentrality, bwb)
            degreeCentrality = {}
            if maxResults:
                degreeCentrality['internal'] = separatedDegreeCentrality['internal'][0:maxResults]
                degreeCentrality['external'] = separatedDegreeCentrality['external'][0:maxResults]
            else:
                degreeCentrality['internal'] = separatedDegreeCentrality['internal']
                degreeCentrality['external'] = separatedDegreeCentrality['external']
                
            separatedBetweenness = self.separateInternalFromExternal(betweenness, bwb)
            betweenness = {}
            if maxResults:
                betweenness['internal'] = separatedBetweenness['internal'][0:maxResults]
                betweenness['external'] = separatedBetweenness['external'][0:maxResults]
            else:
                betweenness['internal'] = separatedBetweenness['internal']
                betweenness['external'] = separatedBetweenness['external']
        else:
            if maxResults:
                inDegree = inDegree[0:maxResults]
                degreeCentrality = degreeCentrality[0:maxResults]
                betweenness = betweenness[0:maxResults]
        
        resultDict = {'inDegree': inDegree,
                      'degreeCentrality': degreeCentrality,
                      'betweenness': betweenness,}
        
        return resultDict
    
    def printSortedResults(self, resultDict):
        inDegree = resultDict['inDegree']
        degreeCentrality = resultDict['degreeCentrality']
        betweenness = resultDict['betweenness']
        cutOff = 60
        
        if type(inDegree) is dict:
            print '\nInternal:'
            for index in range(inDegree['internal'].__len__()):
                print 'In: {0:60} Out: {1:60} Betw: {2:60}'.format(inDegree['internal'][index][:cutOff], 
                                                                   degreeCentrality['internal'][index][:cutOff], 
                                                                   betweenness['internal'][index][:cutOff])
            print '\nExternal:'
            for index in range(inDegree['external'].__len__()):
                print 'In: {0:60} Out: {1:60} Betw: {2:60}'.format(inDegree['external'][index][:cutOff], 
                                                                   degreeCentrality['external'][index][:cutOff], 
                                                                   betweenness['external'][index][:cutOff])
        else:
            for index in range(inDegree.__len__()):
                print 'In: {0:60} Out: {1:60} Betw: {2:60}'.format(inDegree[index][:cutOff], degreeCentrality[index][:cutOff], betweenness[index][:cutOff])
    
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
    
    def orderNodesByInDegree(self, nodes):
        """
        Returns a list of the given nodes, sorted by their indegree.
        
        @param nodes: list of nodes.
        @return: list of ordered nodes.
        """
        # Get the in degree values for the given nodes.
        sortedNodes = [(k, self.inDegree[k]) for k in nodes]
        
        # Sort the nodes and only return the entity descriptions
        sortedNodes.sort(key= lambda x: x[1], reverse=True)
        sortedNodes = [node[0] for node in sortedNodes]
        return sortedNodes
    
    def orderNodesByDegreeCentrality(self, nodes):
        """
        Returns a list of the nodes and their degree centrality values,
        sorted by degree centrality.
        
        @param nodes: list of nodes.
        @return: list of tuples in the form of [(node, degreeCentrality)]
        """
        # Get the degree centrality values for given nodes
        sortedNodes = [(k, self.degreeCentrality[k]) for k in nodes]
        
        # Sort them from large to small, return only node descriptions
        sortedNodes.sort(key= lambda x: x[1], reverse=True)
        sortedNodes = [node[0] for node in sortedNodes]
        return sortedNodes
    
    def orderNodesByBetweenness(self, nodes):
        """
        Returns a list of the nodes and their betweenness centrality values,
        sorted by betweenness centrality.
        
        @param nodes: list of nodes.
        @return: list of tuples in the form of [(node, betweennessCentrality)]
        """
        # Get the betweenness values for given nodes
        sortedNodes = [(k, self.betweenness[k]) for k in nodes]
        
        # Sort them from large to small and only return node names
        sortedNodes.sort(key= lambda x: x[1], reverse=True)
        sortedNodes = [node[0] for node in sortedNodes]
        return sortedNodes
    
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