## An interface for the Dutch legislation using doc.metalex.eu

By Ivan Plantevin, 2013. This project's code can be copied and modified freely.

This is the repo for the code of my Bachelor Thesis project. The goal was to use 
the RDF and XML data on [doc.metalex.eu](http://doc.metalex.eu) to create an interface for the
Dutch legislation on [wetten.nl](http://wetten.nl) that makes use of network analysis and
linked data and to evaluate it. The final web application runs at
[justinian.leibnizcenter.org/wetten](http://justinian.leibnizcenter.org/wetten).

By meeting the requirements and following the steps below, you should be able
to setup and run the web application.

### Requirements

The server side part of the web application runs on django 1.5.1 and uses a couple
of python modules. The application is configured to run with mod_wsgi.
The client side is developed in html5 and makes use of jQuery.
The requirements are as follows:
* Python 2.7.x.
* Apache with mod_wsgi.
* NetworkX python library, see [here](http://networkx.github.io/).
* Modern, non-Internet Explorer browser for front side, javascript enabled.

### Installation – Building and analyzing the network

The three modules that do most of the server side work (except django modules) are 
**CitesParser.py**, **QueryNetwork.py** and **SparqlHelper.py**. CitesParser must be
used to parse the SPARQL results from the metalex server and to build the network from
them. QueryNetwork is then used to perform some degree and centrality measurements on
the network and to store the results by pickling them. The following steps should be
followed:

1. Perform SPARQL queries on the metalex SPARQL endpoint at [http://doc.metalex.eu:8000/test/](http://doc.metalex.eu:8000/test/)
to retrieve the outgoing and incoming citations for the desired laws. The necessary
queries can be found in the module description of CitesParser.
2. Save the xml files resulting from the queries in two folders, one for the incoming
and one for the outgoing citations. Make sure the files start with BWB and end with .xml.
3. Use CitesParser to parse the citations and build the network. Make sure to provide
"inOrOut=both" and "makeNetwork=True". Also provide the (relative) path of the two
folders containing SPARQL results if they aren't located at the default path (default
is "Cites_in" and "Cites_out", both located in the parent folder of the CitesParser
module).
4. Use calcAndPickleAll() from QueryNetwork to calculate and store the in degree, degree centrality
and betweenness centrality.
5. The in degree, degree centrality and betweenness centrality pickle files get a date
and time when stored after their calculation. Make sure to rename or duplicate and rename
them to the file names used by loadMeasurements() in QueryNetwork ("indegree.pickle",
"degree_centrality.pickle" and "betweenness_centrality.pickle").

Done – all network related preparations are complete.

### Installation – Django server

The django setup should go smoothly provided mod_wsgi is used and that it is configured
properly as per the Django documentation. Don't forget to update the Allowed Hosts setting
to contain the domain used.
