from flask import Flask, render_template, jsonify,request
import requests
import time
import datetime
import os.path
import networkx as nx

from key import key_map

app = Flask(__name__)

search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
details_url = "https://maps.googleapis.com/maps/api/place/details/json"
directions_url = 'https://maps.googleapis.com/maps/api/directions/json?'

def buidlBasicGraph(stops):
    print "buidlBasicGraph";
    #tu podstawowyGrafy - same wierzcholki
    #create carGraph and transitGraph
    carFile = open('carGraph.net', 'w')
    transitFile = open('transitGraph.net', 'w')
    carFile.write("*Vertices " + str(len(stops)) + '\n')
    transitFile.write("*Vertices " + str(len(stops)) + '\n')
    i = 0
    for stop in stops:
        carFile.write(str(i) + " \"" + stop + "\"\n")
        transitFile.write(str(i) + " \"" + stop + "\"\n")
        i+=1
    carFile.write("*Arcs " + '\n')
    transitFile.write("*Arcs " + '\n')
    carFile.close()
    transitFile.close()

def addEdgeTograph(edgeCar,edgeTransit, stopFrom, stopTo):
    #tu dodajemy krawedz
    if(edgeCar != {}):
        carFile = open('carGraph.net', 'a')
        carFile.write(str(stopFrom) + " " + str(stopTo) + " " + str(edgeCar['duration']) + '\n')
        carFile.close()

    if(edgeTransit != {}):
        carFile = open('transitGraph.net', 'a')
        carFile.write(str(stopFrom) + " " + str(stopTo) + " " + str(edgeTransit['duration']) + '\n')
        carFile.close()

def readStops():
	print "readStops";
	file = open('przystanki.txt', 'r')
	stopsTemp = file.readlines()
	stops = []
	for stop in stopsTemp:
		stop = stop.replace("\n","")
		if(stop!=""):
			stops.append(stop)
	file.close()
	return stops

def checkIsFileExist(fname):
	return os.path.isfile(fname)

#Funkcja do zapisu grafu
#zapisywany plik graph_RRMMDDGGMM jesli aktualny czas jest +-5 min to nie pobieraj danych tylko historyczny graf
def saveGraph(graph):
	print "saveGraph";
	now = datetime.datetime.now()
	fileName = 'graph_'+ now.year +now.month + now.day + now.minute
	#save
	return graph

def loadGraph():
	print "loadGraph";
	now = datetime.datetime.now()
	fileName = 'graph_' + now.year + now.month + now.day + now.minute
	#load-regex
	i=0
	graph = 1
	for i in 6:
		day = now.day - i
		fileName = 'graph_' + now.year + now.month + day + now.minute
		if (checkIsFileExist(fileName)):
			#zaladuj plik na podstawie nazwy poniewaz istnieje plik nie starszy niz 5 minut
			return graph
	graph = 1
	return "null"


#Analiza czy istnieje krawedz pomiedzy przystankami
def analizeSteps(steps):
	if (len(steps) == 1):
		return True
	elif (len(steps) > 3 or len(steps) == 0):
		return False
	else:
		countTransit = 0
		return True
		for step in steps:
			if (step=='TRANSIT'):
				countTransit=countTransit+1
		if(countTransit>1):
			return False;
		else:
			return True

def createGraph():
    stopsList = readStops()
    buidlBasicGraph(stopsList)

    size = len(stopsList)
    start = time.time()
    j = 0
    for x in stopsList:
        i = 0
        for i in range(size):
            queryFrom = x
            queryTo = stopsList[i]
            result = {}
            # JESLI TO SAMO TO POMIN
            if (queryFrom == queryTo):
                edgeTransit = {}
                edgeCar = {}
                continue

            search_payloadCar = {"origin": queryFrom, 'destination': queryTo, "key": key_map}
            search_reqCar = requests.get(directions_url, params=search_payloadCar)
            search_jsonCar = search_reqCar.json()

            if (len(search_jsonCar["routes"]) != 0):

                search_payloadTransit = {"origin": queryFrom, 'destination': queryTo, "mode": 'transit', "key": key_map}
                search_reqTransit = requests.get(directions_url, params=search_payloadTransit)
                search_jsonTransit = search_reqTransit.json()

                if (len(search_jsonTransit["routes"]) != 0):
                    destCar = search_jsonCar["routes"][0]['legs']
                    destTransit = search_jsonTransit["routes"][0]['legs']
                    # Uwaga na stepy - nalezy w takim przypadku usunac krawedz
                    # Czas in s
                    # Dystans in m
                    edgeCar = {'distance': destCar[0]['distance']['value'], 'duration': destCar[0]['duration']['value']}
                    transitSteps = destTransit[0]['steps']
                    if (analizeSteps(transitSteps)):
                        edgeTransit = {'distance': destTransit[0]['distance']['value'],
                                       'duration': destTransit[0]['duration']['value']}
                    else:
                        edgeTransit = {}

                    result['success'] = "success"
                else:
                    edgeTransit = {}
                    edgeCar = {}
                    result['error'] = "null poineter"
            else:
                edgeTransit = {}
                edgeCar = {}
                result['error'] = "null poineter"

            addEdgeTograph(edgeCar, edgeTransit, j, i)
            i = i + 1
        j = j + 1
    end = time.time()
    print "Duration: ", end - start, "\n"
  #  return jsonify(result)

def getTheBestTransportMode(stopFrom, stopTo):
    mode = {}

    g = nx.read_pajek("carGraph.net")
    gCarD = g.to_directed()
    carLength, carPath = nx.bidirectional_dijkstra(gCarD, stopFrom, stopTo)
    print "car Len: " + str(carLength)
    print "car path: " + str(carPath)

    g1 = nx.read_pajek("transitGraph.net")
    gTransitD = g1.to_directed()
    try:
        transitLength, transitPath = nx.bidirectional_dijkstra(gTransitD, stopFrom, stopTo)
        print "trans Len: " + str(transitLength)
        print "trans path: " + str(transitPath)
        if(transitLength <= carLength):
            mode = {"vehicle": "transit", 'length': transitLength, "path": transitPath}
        else:
            mode = {"vehicle": "car", 'length': carLength, "path": carPath}
    except nx.NetworkXNoPath:
        mode = {"vehicle": "car", 'length': carLength, "path": carPath}
        print 'NO PATH'

    return mode

@app.route("/", methods=["GET"])
def retreive():
    return render_template('layout.html')

@app.route("/sendRequest", methods=['GET'])
def results():
    result = {}
    paramqueryFrom = request.args.get('queryFrom').encode('utf-8')
    paramqueryTo = request.args.get('queryTo').encode('utf-8')
    stopsList = readStops()
    # tu mozna dodac sprawdzenie czy nazwy znajduja sie na listach przystankow
    # jak nie to zakoncz
    if(str(paramqueryFrom) not in stopsList or str(paramqueryTo) not in stopsList):
        result['error'] = "Punkt poczatkowy oraz koncowy trasy musi znajdowac sie na liscie przystankow!"

    #analyze graph networkx
    transportMode = getTheBestTransportMode(str(paramqueryFrom), str(paramqueryTo))
    print transportMode
    print "\n--- Wybrano: ---"
    print transportMode['vehicle']
    print transportMode['length']
    print transportMode['path']
    # mode = {"vehicle": "transit", 'length': transitLength, "path": transitPath}

    result['success'] = "success"
    return jsonify(result)

if __name__ ==  "__main__":
    createGraph()
    app.run(debug=True)
