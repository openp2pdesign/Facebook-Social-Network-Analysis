# coding: utf-8
#
# Social Network Analysis of a Facebook group friendships
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: GPL v.3
#
# Requisite: 
# install requests with pip install requests
# install json with pip install json
# install NetworkX with pip install networkx
#

import requests
import json
import networkx as nx

G=nx.Graph()

# Some group examples:
# Fabber in Italia
fii = "192759480789364"
# Fab9
fab9 = "152023668302761"

group = fab9
base_url = 'https://graph.facebook.com/'+group+'/members'

# How to get an infinite access token, otherwise our analysis takes too long
#
# Go to https://developers.facebook.com/tools/explorer/ to get the normal access token
#
# as said here: https://developers.facebook.com/docs/facebook-login/access-tokens/#extending
#
# Create an application and get API key and secret, and do this:
#
# GET /oauth/access_token?  
#    grant_type=fb_exchange_token&           
#    client_id={app-id}&
#    client_secret={app-secret}&
#    fb_exchange_token={short-lived-token} 
#
# This is done by the following code:
#

ACCESS_TOKEN = "Insert here"
client_id="Insert here"
client_secret="Insert here"

base_url0 = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % \
    (client_id, client_secret, ACCESS_TOKEN,)
message = requests.get(base_url0)
message1 = message.content[13:]
INFINITE_TOKEN = message1[:message1.find("&expires=")]
print "The infinite token is:",INFINITE_TOKEN

# Then access Facebook with the infinite token
ACCES_TOKEN = INFINITE_TOKEN

# Get only the ID of the group users in order to get all of them
fields = '&fields=id&limit=5000'
url = '%s?fields=%s&access_token=%s' % \
    (base_url, fields, ACCESS_TOKEN,)

# Interpret the response as JSON and convert back
# to Python data structures
print "Talking to the API..."
content = requests.get(url).json()


#############################
print "FRIENDSHIPS ON A FACEBOOK GROUP"
print ""

# Get the names of the users
for i,k in enumerate(content["data"]):

	base_url3 = 'https://graph.facebook.com/'+k["id"]
	fields3 = '&limit=2000'
	url3 = '%s?fields=%s&access_token=%s' % (base_url3, fields3, ACCESS_TOKEN,)	
	firstname = requests.get(url3).json()
	X = firstname["name"]
	print "----------------------"
	print "Check the friends of",X

	for j,m in enumerate(content["data"]):
		base_url2 = 'https://graph.facebook.com/'+k["id"]+'/friends/'+m["id"]
		url2 = '%s?access_token=%s' % (base_url2, ACCESS_TOKEN,)	
		name = requests.get(url2).json()
		if len(name["data"]) != 0:
			Y = name["data"][0]["name"]
			#print type(X), type(Y)
			print "- Friend with",Y
			G.add_edge(X,Y)
		
print ""
print "The group was analyzed succesfully."
print ""
print "Saving the file as "+group+"-friendships.gexf..."
nx.write_gexf(G, group+"-friendships.gexf")
