#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Add files to path
import os
import sys
viewsDir = os.path.dirname(__file__)
wettenDir = os.path.abspath(os.path.join(viewsDir, '../../')) + '/'
sys.path.append(wettenDir)

from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, redirect
from django.utils import simplejson as json
import urllib2
import QueryNetwork as QN
import CitesParser as CP
import SparqlHelper as sparql
import re
import pickle

def index(request):
    return redirect('/wetten/doc/BWBR0011353')

def doc(request, document):
    citesParser = CP.CitesParser();
    sparqlHelper = sparql.SparqlHelper()
    # List of BWB's in the subset
    bwbDocuments = ['BWBR0002226', 
                    'BWBR0002227', 
                    'BWBR0002320', 
                    'BWBR0005537', 
                    'BWBR0011353', 
                    'BWBR0027018']
    pageTitle = citesParser.entityDescription(document)
    
    bwb_links = []
    for bwbDocument in bwbDocuments:
        bwb_links.append(sparqlHelper.getLatestTitleAndExpressionForBWB(bwbDocument))
    
    # If only BWB number is provided , redirect to latest expression for BWB
    if re.match('BWBR\d{7}$', document):
        work = 'http://doc.metalex.eu/id/' + document
        latestExpression = sparqlHelper.latestExpressionForWork(work)
        return redirect(sparqlHelper.wettenDocForId(latestExpression))
    else:
        metalexData = urllib2.urlopen('http://doc.metalex.eu/doc/' + document)
    metalexXML = metalexData.read()
    
    # Get all versions for document
    work = 'http://doc.metalex.eu/id/' + re.sub('/nl/.*','', document)
    expressions = sparqlHelper.getExpressionsForWork(work)
    docExpressions = sparqlHelper.wettenDocsForIds(expressions)
    dates = sparqlHelper.datesForExpressions(docExpressions)
    
    # The date for the currently viewed document
    currentDateTuple = sparqlHelper.dateForExpression(document)
    
    # Make the string showing date information
    # If the current date isn't the most recent one, display message
    mostRecentDate = sparqlHelper.dateForExpression(dates['expressions'][dates['dates'][0]])[0]
    if currentDateTuple[0] < mostRecentDate:
        dateInfo = 'Huidige versie: ' + currentDateTuple[1] + ' – Let op: nieuwere versie beschikbaar!'
    else:
        dateInfo = 'Huidige versie: ' + currentDateTuple[1] + ' – Dit is de nieuwste versie.'
    
    
    context = {'metalexXML': metalexXML, 
               'bwb_links': bwb_links, 
               'title': pageTitle,
               'expressions': dates['expressions'],
               'dates': dates['dates'],
               'current': currentDateTuple[1],
               'dateInfo': dateInfo, }
    
    return render(request, 'wetten/doc.html', context)

def bwb(request):
    referer = request.META.get('HTTP_REFERER')
    maxResults = int(request.GET.get('maxResults'))
    bwb = re.search('BWBR\d{7}', referer).group(0)
    query = QN.QueryNetwork()
    sortedData = query.sortEntitiesForBWB(bwb, maxResults)
    human_descriptions = pickle.load(open(wettenDir + 'human_descriptions.pickle', 'r'))

    # Render div's for in degree
    template = loader.get_template('wetten/important_for_bwb.html')
    context = Context({'entities': sortedData['inDegree'],
                       'descriptions': human_descriptions,})
    inDegree = template.render(context)
    
    # Render div's for degree centrality
    context = Context({'entities': sortedData['degreeCentrality'],
                       'descriptions': human_descriptions,})
    degreeCentrality = template.render(context)
    
    # Render div's for betweenness centrality
    context = Context({'entities': sortedData['betweenness'],
                       'descriptions': human_descriptions,})
    betweenness = template.render(context)
    
    return HttpResponse(json.dumps({'inDegree': inDegree, 
                                    'degreeCentrality': degreeCentrality,
                                    'betweenness': betweenness,}))

def related(request):
    parser = CP.CitesParser()
    human_descriptions = pickle.load(open(wettenDir + 'human_descriptions.pickle'))
    bwb_titles = pickle.load(open(wettenDir + 'bwb_titles.pickle'))
    
    entity = request.GET.get('entity')
    maxResults = int(request.GET.get('maxResults'))
    entityDescriptionData = parser.entityDescription(entity, True)
    entityDescription = entityDescriptionData[0]
    if entityDescriptionData[2]:
        humanDescription = parser.humanDescriptionForEntity(entityDescriptionData[2])
    else:
        humanDescription = entityDescriptionData[1]
        
    if entityDescription:
        query = QN.QueryNetwork()
        
        if not query.entityIsInGraph(entityDescription):
            return HttpResponse(json.dumps({'success': False, 'current_selection': humanDescription,}))
        
        relatedEntities = query.sortRelatedEntities(entityDescription, maxResults)  
        
        internal = {}
        external = {}
        # Render div's for internal sources for in-degree
        template = loader.get_template('wetten/related.html')
        context = Context({'entities': relatedEntities['inDegree']['internal'],
                           'descriptions': human_descriptions,
                           'bwb_titles': False,})
        internal['inDegree'] = template.render(context)
        
        # Render div's for internal sources for degree centrality
        context = Context({'entities': relatedEntities['degreeCentrality']['internal'],
                           'descriptions': human_descriptions,
                           'bwb_titles': False,})
        internal['degreeCentrality'] = template.render(context)
        
        # Render div's for internal sources for betweenness centrality
        context = Context({'entities': relatedEntities['betweenness']['internal'],
                           'descriptions': human_descriptions,
                           'bwb_titles': False,})
        internal['betweenness'] = template.render(context)
        
        # Render div's for external sources for in-degree
        context = Context({'entities': relatedEntities['inDegree']['external'],
                           'descriptions': human_descriptions,
                           'bwb_titles': bwb_titles})
        external['inDegree'] = template.render(context)
        
        # Render div's for external sources for degree centrality
        context = Context({'entities': relatedEntities['degreeCentrality']['external'],
                           'descriptions': human_descriptions,
                           'bwb_titles': bwb_titles})
        external['degreeCentrality'] = template.render(context)
        
        # Render div's for external sources for betweenness centrality
        context = Context({'entities': relatedEntities['betweenness']['external'],
                           'descriptions': human_descriptions,
                           'bwb_titles': bwb_titles})
        external['betweenness'] = template.render(context)
        
        data = {'success': True,
               'internal': internal,
               'external': external,
               'current_selection': humanDescription,
               }
        
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponse(json.dumps({'success': False, 'current_selection': 'onbekend',}))
    
def relatedContent(request):
    sparqlHelper = sparql.SparqlHelper()
    entity = request.GET.get('entity')
    referer = request.META.get('HTTP_REFERER')
    currentDate = re.search('\d\d\d\d-\d\d-\d\d', referer).group(0)
    
    dateData = sparqlHelper.getBestDocForEntity(entity, currentDate)
    # No expression found, return error
    if not dateData:
        return HttpResponse('error')

    data = metalexAndVersions(dateData, sparqlHelper)
    
    return HttpResponse(json.dumps(data))

def reference(request):
    sparqlHelper = sparql.SparqlHelper()
    about = request.GET.get('about')
    referer = request.META.get('HTTP_REFERER')
    currentDate = re.search('\d\d\d\d-\d\d-\d\d', referer).group(0)
    dateData = sparqlHelper.getBestCitedExpressionForReference(about, currentDate)
    
    # No expressions found, return error
    if not dateData:
        return HttpResponse('error')
    
    data = metalexAndVersions(dateData, sparqlHelper)
    
    return HttpResponse(json.dumps(data))
    
def metalexAndVersions(dateData, sparqlHelper):
    expressions = dateData['expressions']
    dates = dateData['dates']
    current = dateData['bestDate']
    
    bestExpression = expressions[current]
    print '\n\nBest expression: '+ bestExpression
    
    metalexData = urllib2.urlopen(bestExpression)
    metalexXML = metalexData.read()
    
    currentDate = sparqlHelper.dateForExpression(bestExpression)[0]
    mostRecentDate = sparqlHelper.dateForExpression(expressions[dates[0]])[0]
    if currentDate < mostRecentDate:
        dateInfo = 'Getoonde versie: ' + current + ' – Let op: nieuwere versie beschikbaar!'
    else:
        dateInfo = 'Getoonde versie: ' + current + ' – Dit is de nieuwste versie.'
    
    template = loader.get_template('wetten/detail_versions.html')
    context = Context({'dates': dates,
                       'expressions': expressions,
                       'current': current,})
    
    versions = template.render(context)
    
    # Expression for law of which retrieved document is part of
    bwb = re.search('BWBR\d{7}', bestExpression)
    if bwb:
        dateString = re.search('\d\d\d\d-\d\d-\d\d', bestExpression).group(0)
        bwbExpression = '/wetten/doc/' + bwb.group(0) + '/nl/' + dateString + '/data.xml'
        link = '<a class="open_bwb" href="'+ bwbExpression +'" target="_blank">Open bijbehorende wet in nieuw venster.</a>'
        print 'The link: '+ link
        metalexXML = link + metalexXML
    
    return {'metalex': metalexXML,
            'versions': versions,
            'dateInfo': dateInfo}
    
def timetravelArticle(request):
    parser = CP.CitesParser()
    about = request.GET.get('about')
    
    # Get referer to extract its date later on
    referer = request.META.get('HTTP_REFERER') 
    
    entityDescription = parser.entityDescription(about)
    if entityDescription:
        work = parser.workLevelURI(about, entityDescription)[0]
        sparqlHelper = sparql.SparqlHelper()
        expressions = sparqlHelper.getExpressionsForWork(work)
        docExpressions = sparqlHelper.getDocsForIds(expressions)
        dates = sparqlHelper.datesForExpressions(docExpressions)
        
        # The date for the currently viewed document
        currentDateTuple = sparqlHelper.dateForExpression(referer)
        
        # Render the results.
        template = loader.get_template('wetten/timetravelArticle.html')
        context = Context({'expressions': dates['expressions'],
                           'dates': dates['dates'],
                           'current': currentDateTuple[1]})
        versions = template.render(context)
        
        return HttpResponse(versions)
    else:
        return HttpResponse('Er is een fout opgetreden.')
    
def timetravelParagraph(request):
    sparqlHelper = sparql.SparqlHelper()
    about = request.GET.get('about')
    
    # Get referer to extract its date later on
    referer = request.META.get('HTTP_REFERER') 
    
    currentDate = re.search('\d\d\d\d-\d\d-\d\d', referer).group(0)
    versionData = sparqlHelper.differingExpressionsForHash(about, currentDate)
    
    # The date for the currently viewed document
    currentDateTuple = sparqlHelper.dateForExpression(referer)
    
    # Render the results.
    template = loader.get_template('wetten/timetravelArticle.html')
    context = Context({'expressions': versionData['expressions'],
                       'dates': versionData['dates'],
                       'current': currentDateTuple[1]})
    versions = template.render(context)
    
    return HttpResponse(versions)
    

def metalexContent(request):
    expression = request.GET.get('expression')
    
    metalexData = urllib2.urlopen(expression)
    metalexXML = metalexData.read()
    
    # Expression for law of which retrieved document is part of
    bwb = re.search('BWBR\d{7}', expression)
    if bwb:
        dateString = re.search('\d\d\d\d-\d\d-\d\d', expression).group(0)
        bwbExpression = '/wetten/doc/' + bwb.group(0) + '/nl/' + dateString + '/data.xml'
        link = '<a class="open_bwb" href="'+ bwbExpression +'" target="_blank">Open bijbehorende wet in nieuw venster.</a>'
        print 'The link: '+ link
        metalexXML = link + metalexXML
    
    return HttpResponse(metalexXML)
