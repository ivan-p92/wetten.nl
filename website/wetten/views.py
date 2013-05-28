#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render
from django.utils import simplejson as json
import urllib2
import QueryNetwork as QN
import CitesParser as CP
import SparqlHelper as sparql
import re
import pickle

def index(request):
    return HttpResponse("Gebruiksinfo")

def doc(request, document):
    citesParser = CP.CitesParser();
    sparqlHelper = sparql.SparqlHelper()
    humanDescriptions = pickle.load(open('/Users/Ivan/Documents/Beta-gamma/KI jaar 2/Afstudeerproject/Project/Python/wetten.nl/human_descriptions.pickle', 'r'))
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
    
    metalexData = urllib2.urlopen('http://doc.metalex.eu/doc/' + document)
    metalexXML = metalexData.read()
    bwb = re.findall('BWBR\d{7}', document)[0]
    
    query = QN.QueryNetwork()
    entities = query.sortEntitiesForBWB(bwb)
    
    context = {'metalexXML': metalexXML, 
               'entities': entities, 
               'bwb_links': bwb_links, 
               'descriptions': humanDescriptions,
               'title': pageTitle}
    return render(request, 'wetten/doc.html', context)

def related(request):
    parser = CP.CitesParser()
    human_descriptions = pickle.load(open('/Users/Ivan/Documents/Beta-gamma/KI jaar 2/Afstudeerproject/Project/Python/wetten.nl/human_descriptions.pickle'))
    bwb_titles = pickle.load(open('/Users/Ivan/Documents/Beta-gamma/KI jaar 2/Afstudeerproject/Project/Python/wetten.nl/bwb_titles.pickle'))
    
    entity = request.GET.get('entity')
    entityDescription = parser.entityDescription(entity)
    if entityDescription:
        query = QN.QueryNetwork()
        
        if not query.entityIsInGraph(entityDescription):
            return HttpResponse(json.dumps({'success': False}))
        
        relatedEntities = query.sortRelatedEntities(entityDescription)  
        
        # Render div's for internal sources
        template = loader.get_template('wetten/related.html')
        context = Context({'entities': relatedEntities['internal'],
                           'descriptions': human_descriptions,
                           'bwb_titles': False})
        internal = template.render(context)
        
        # Render div's for external sources
        context = Context({'entities': relatedEntities['external'],
                           'descriptions': human_descriptions,
                           'bwb_titles': bwb_titles})
        external = template.render(context)
        
        data = {'success': True,
               'internal': internal,
               'external': external
               }
        
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponse(json.dumps({'success': False}))
    
def relatedContent(request):
    sparqlHelper = sparql.SparqlHelper()
    entity = request.GET.get('entity')
    
    # Get latest expression
    expression = sparqlHelper.getLatestDocForEntity(entity)
    metalexData = urllib2.urlopen(expression)
    metalexXML = metalexData.read()
    
    return HttpResponse(metalexXML)

def reference(request):
    sparqlHelper = sparql.SparqlHelper()
    about = request.GET.get('about')
    idExpression = sparqlHelper.getLatestCitedExpressionForReference(about)
    citedExpression = sparqlHelper.getDocForId(idExpression)
    metalexData = urllib2.urlopen(citedExpression)
    metalexXML = metalexData.read()
    
    return HttpResponse(metalexXML)
    
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
    
    return HttpResponse(metalexXML)