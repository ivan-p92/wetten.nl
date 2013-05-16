from django.http import HttpResponse
from django.shortcuts import render
import urllib2

def index(request):
    return HttpResponse("Gebruiksinfo")

def doc(request, document):
    
    metalexData = urllib2.urlopen('http://doc.metalex.eu/doc/' + document)
    metalexXML = metalexData.read()
    metalexXML.replace('<?xml version="1.0" encoding="utf-8"?>','')
    metalexXML.replace('<?xml-stylesheet type="text/css" href="http://doc.metalex.eu/static/css/metalex.css"?>', '')

    context = {'metalexXML': metalexXML}
    return render(request, 'wetten/doc.html', context)
