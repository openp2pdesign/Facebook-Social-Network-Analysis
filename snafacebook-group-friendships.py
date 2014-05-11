# -*- encoding: utf-8 -*-
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
from time import sleep
import os

# Clear screen
os.system('cls' if os.name=='nt' else 'clear')

graph=nx.Graph()

# Some group examples:
# Fabber in Italia
fii = "192759480789364"
# Fab9
fab9 = "152023668302761"
# Maind
maind = "51802632393"

group = fii
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



print ""
print "....................................................."
print "FRIENDSHIPS ON A FACEBOOK GROUP"
print ""

base_url0 = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % \
    (client_id, client_secret, ACCESS_TOKEN,)
message = requests.get(base_url0)
message1 = message.content[13:]
INFINITE_TOKEN = message1[:message1.find("&expires=")]
print "The infinite token is:",INFINITE_TOKEN

# Get only the ID of the group users in order to get all of them
fields = '&fields=id&limit=5000'
url = '%s?fields=%s&access_token=%s' % \
    (base_url, fields, INFINITE_TOKEN)

# Interpret the response as JSON and convert back
# to Python data structures
print ""
print "Talking to the API..."
content = requests.get(url).json()

print ""
print "Getting all the users..."

# Get the users and the connections between the users
for i,k in enumerate(content["data"]):

	base_url3 = 'https://graph.facebook.com/'+k["id"]
	fields3 = '&limit=2000'
	url3 = '%s?fields=%s&access_token=%s' % (base_url3, fields3, INFINITE_TOKEN)	
	
	try:
		firstname = requests.get(url3).json()
	except:
		name1 = requests.get(url3)
		firstname = json.loads(name1.text.strip("'<>() ").replace('\'', '\"'))
	
	# Print debug information
	print ""
	print "----------------------"
	print ""
	print "New user:"
	print
	print firstname

	if "error" in firstname:
		# Check if we reached the API limit
		if firstname["error"]["message"] == "User request limit reached.":
			# Wait 30 minutes if we reach the user limit
			# See https://developers.facebook.com/docs/reference/ads-api/api-rate-limiting/
			print ""
			print "There was an error. Waiting 30 minutes before starting again..."
			sleep(60*30)
			firstname = requests.get(url3).json()
		# Check if we got another error which I haven't understood yet ...
		elif firstname["error"]["message"] == "Unsupported get request.":
			print ""
			print "There is an error with this user."

	else:
		# Add node with gender data	
		X = firstname["name"]
		graph.add_node(X)
		if "gender" in firstname:
			graph[X]['gender']=firstname["gender"]
		else:
			graph[X]['gender']= "None"
	
		# Check friendships with the other members of the group
		print ""
		print "Check the friends of",X

		for j,m in enumerate(content["data"]):
			base_url2 = 'https://graph.facebook.com/'+k["id"]+'/friends/'+m["id"]
			url2 = '%s?access_token=%s' % (base_url2, INFINITE_TOKEN)	
			try:
				name = requests.get(url2).json()
			except:
				name1 = requests.get(url2)
				name = json.loads(name1.text.strip("'<>() ").replace('\'', '\"'))
			if len(name["data"]) != 0:
				print ""
				print name
			if "data" in name and len(name["data"]) != 0:
				Y = name["data"][0]["name"]
				#print type(X), type(Y)
				print "- Friend with",Y
				graph.add_edge(X,Y)
	
# Save the file and exit	
print ""
print "The group was analyzed succesfully."
print ""
print "Saving the file as "+group+"-friendships.gexf..."
nx.write_gexf(graph, group+"-friendships.gexf")
