#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render
import urllib2
import QueryNetwork as QN
import CitesParser as CP

def index(request):
    return HttpResponse("Gebruiksinfo")

def doc(request, document):
    
    metalexData = urllib2.urlopen('http://doc.metalex.eu/doc/' + document)
    metalexXML = metalexData.read()
    metalexXML.replace('<?xml version="1.0" encoding="utf-8"?>','')
    metalexXML.replace('<?xml-stylesheet type="text/css" href="http://doc.metalex.eu/static/css/metalex.css"?>', '')

    context = {'metalexXML': metalexXML}
    return render(request, 'wetten/doc.html', context)

def related(request):
    parser = CP.CitesParser()
    entity = request.GET.get('entity')
    entityDescription = parser.entityDescription(entity)
    if entityDescription:
        return HttpResponse(entity + '\n\nDescription: ' + entityDescription)
    else:
        return HttpResponse(entity)