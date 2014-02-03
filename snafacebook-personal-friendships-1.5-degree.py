# -*- encoding: utf-8 -*-
#
# Social Network Analysis of a Facebook user friendships
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
import sys
from time import sleep
import os

# Clear screen
os.system('cls' if os.name=='nt' else 'clear')

graph=nx.Graph()

usernameurl = "massimo.menichinelli"
base_url = "https://graph.facebook.com/"+usernameurl

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


print ""
print "....................................................."
print "FRIENDSHIPS OF A FACEBOOK USER"
print ""

base_url0 = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % \
    (client_id, client_secret, ACCESS_TOKEN,)
message = requests.get(base_url0)
message1 = message.content[13:]
INFINITE_TOKEN = message1[:message1.find("&expires=")]
print "The infinite token is:",INFINITE_TOKEN

# Then access Facebook with the infinite token
ACCES_TOKEN = INFINITE_TOKEN

# Interpret the response as JSON and convert back
# to Python data structures
print ""
print "Talking to the API..."
content = requests.get(base_url).json()

print ""
print "Analyzing the personal network of",content["first_name"],content["last_name"], "(id =", content["id"],", gender =",content["gender"],")."

friends_url = "https://graph.facebook.com/"+content["id"]+"/friends"

# Get only the ID of the group users in order to get all of them
fields = '&fields=id&limit=5000'
url = '%s?fields=%s&access_token=%s' % \
    (friends_url, fields, ACCESS_TOKEN,)

friends = requests.get(url).json()

if "error" in content.keys():
	print
	print "Error:",friends["error"]
	print
	exit()	

users = {}

# Get the names of the users
print ""
print "Getting the name of the users in the network..."
print ""	

for i,k in enumerate(friends["data"]):
	# Get the name of the first user
	url3 = "https://graph.facebook.com/"+friends["data"][i]["id"]
	name1 = requests.get(url3).json()
	first_name = name1["name"]
	
	for l in friends["data"]:
		# Get the name of the second user
		url4 = "https://graph.facebook.com/"+l["id"]
		name2 = requests.get(url4).json()
		second_name = name2["name"]
		sleep(2)
		
		if first_name != second_name:		
			print ""
			print "Checking the connection between",first_name,"and",second_name
			sleep(2)
			# Get the mutual friends of first and second user
			base_url2 = 'https://graph.facebook.com/fql?q=SELECT uid2 FROM friend WHERE uid1="'+friends["data"][i]["id"]+'" and uid2="'+l["id"]+'"'
			#base_url2 = 'https://graph.facebook.com/'+friends["data"][i]["id"]+'/mutualfriends/'+l["id"]
			url2 = '%s&access_token=%s' % (base_url2, ACCESS_TOKEN,)	
			names = requests.get(url2).json()
			
			# Add edge
			if "data" in names.keys() and len(names["data"]) != 0:
				graph.add_edge(first_name,second_name)
				print "-",first_name,"and",second_name,"are friends."
		

print ""
print "The personal profile was analyzed succesfully."
print ""
print "Saving the file as "+usernameurl+"-personal-network-1.5-degree.gexf..."
nx.write_gexf(graph, usernameurl+"-personal-network-1.5-degree.gexf")
