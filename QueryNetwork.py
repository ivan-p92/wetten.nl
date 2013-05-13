'''
Created on 9 mei 2013

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
        
    def getDegree(self, node):
        return self.degree[node]
    
    def calcAndPickleDegree(self):
        t = time.time()
        self.degree = nx.degree(self.G)
        print 'Degree calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.degree, open('degree.pickle', 'w'))
        
    def calcAndPickleDegreeCentrality(self):
        t = time.time()
        self.degreeCentrality = nx.degree_centrality(self.G)
        print 'Degree centrality calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.degreeCentrality, open('degree_centrality.pickle', 'w'))
        
    def calcAndPickleBetweenness(self):
        t = time.time()
        self.betweenness = nx.betweenness_centrality(self.G)
        print 'Betweenness centrality calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.betweenness, open('betweenness_centrality.pickle', 'w'))
        
    def calcAndPickleEigenvector(self):
        t = time.time()
        self.eigenvector = nx.eigenvector_centrality(self.G, max_iter=1000)
        print 'Eigenvector centrality calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.eigenvector, open('eigenvector_centrality.pickle', 'w'))
        
    def calcAndPickleLoadCentrality(self):
        t = time.time()
        self.loadCentrality = nx.load_centrality(self.G)
        print 'Load centrality calculation time: ' + str(int(time.time() - t)) + ' seconds'
        pickle.dump(self.loadCentrality, open('load_centrality.pickle', 'w'))
    
    def loadMeasurements(self):
        t = time.time()
        self.degree = pickle.load(open('degree.pickle', 'r'))
        self.degreeCentrality = pickle.load(open('degree_centrality.pickle', 'r'))
        self.betweenness = pickle.load(open('betweenness_centrality.pickle', 'r'))
#         self.eigenvector = None
        self.loadCentrality = pickle.load(open('load_centrality.pickle', 'r'))
        print 'Loaded measurements in ' + str(int(time.time() - t)) + ' seconds'
        self.didLoadMeasurements = True
        
    def getNodesForBWB(self, bwb):
        r = re.compile(bwb + '/.*')
        nodes = filter(r.match, self.G.nodes())
        return nodes
    
    def getNeighboursForEntity(self, entity):
        return self.G.neighbors(entity)
    
    def getRelatedEntities(self, entity):
        directNeighbours = self.getNeighboursForEntity(entity)
        if not directNeighbours:
            return False
        
        indirectNeighbours = []
        for neighbour in directNeighbours:
            indirectNeighbours += self.getNeighboursForEntity(neighbour)
            
        return list(set(directNeighbours + indirectNeighbours))
    
    def sortRelatedEntities(self, entity):
        if not self.didLoadMeasurements:
            self.loadMeasurements()
        
        relatedEntities = self.getRelatedEntities(entity)
        if not relatedEntities:
            return []
        
        degreeCentrality = self.orderNodesByDegreeCentrality(relatedEntities)
        betweenness = self.orderNodesByBetweenness(relatedEntities)
        print '\nDegree centralities:\n' + str(degreeCentrality)
        print '\n\nBetweenness centralities:\n' + str(betweenness)
        
        degreeIndices = {}
        betweennessIndices = {}
        for i in range(len(degreeCentrality)):
            degreeIndices[degreeCentrality[i][0]] = i
        for i in range(len(betweenness)):
            betweennessIndices[betweenness[i][0]] = i
            
        mergedIndices = [(k, degreeIndices[k], betweennessIndices[k]) for k in degreeIndices.keys()]
        sortedEntities = sorted(mergedIndices, key = lambda x: x[1] + x[2])
        
        degreeCentrality = dict(degreeCentrality)
        betweenness = dict(betweenness)
        for entity in sortedEntities:
            print entity[0] + ', \t\t' + str(degreeCentrality[entity[0]]) + ', \t' + str(betweenness[entity[0]])
        
        return [entity[0] for entity in sortedEntities]
    
    def orderNodesByDegree(self, nodes):
        
        # First get the subset of the nodes in self.degree
        degree = [(k, self.degree[k]) for k in nodes]
        degree.sort(key= lambda x: x[1], reverse=True)
        return degree
    
    def orderNodesByDegreeCentrality(self, nodes):
        
        # First get the subset of the nodes in self.degree
        result = [(k, self.degreeCentrality[k]) for k in nodes]
        result.sort(key= lambda x: x[1], reverse=True)
        return result
    
    def orderNodesByBetweenness(self, nodes):
        
        result = [(k, self.betweenness[k]) for k in nodes]
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