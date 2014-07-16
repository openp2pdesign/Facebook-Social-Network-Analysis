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
# Another option to consider:
# http://datajournalismi.blogspot.it/2013/10/social-network-analysis-of-ones.html

import requests
import json
import networkx as nx
from time import sleep
import itertools
import os

# From http://stackoverflow.com/a/312467
def split_seq(iterable, size):
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))


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
group = maind
base_url = 'https://graph.facebook.com/v1.0/'+group+'/members'

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

end_point = "https://graph.facebook.com/v1.0/"

batch_request = ""

users = []

newpage = {}
i = 0
newpage[0] = requests.get(url).json()

while 1 > 0:
	print "-----------------------------------------"
	print "Reading page n.", i,"from the Facebook API..."
	print ""
	if i != 0:
		newpage[i] = requests.get(newpage[i-1]["paging"]["next"]).json()
	if len(newpage[i]["data"]) == 0:
		print "Got all the data."
		break
	if "paging" in newpage[i].keys():
		for w,x in enumerate(newpage[i]["data"]):
			users.append(x)

	i = i + 1

print ""
print "There are",len(users),"users."

# Get the users and the connections between the users
for i,k in enumerate(users):
	base_url3 = 'https://graph.facebook.com/v1.0/'+k["id"]
	fields3 = '&limit=2000'
	url3 = '%s?fields=%s&access_token=%s' % (base_url3, fields3, INFINITE_TOKEN)	
	
	try:
		firstname = requests.get(url3).json()
	except:
		name1 = requests.get(url3)
		firstname = json.loads(name1.text.strip("'<>() ").replace('\'', '\"'))

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

		# Print debug information
        	print ""
        	print "----------------------"
        	print ""
		X = firstname["name"].encode("utf-8")
        	print "New user:", X
        	print
        	# Debug
        	# print firstname

		# Add node with gender data
		if X not in graph.nodes():
			graph.add_node(X)
		if "gender" in firstname:
			graph.node[X]['gender']=firstname["gender"]
			print X,"is a",graph.node[X]['gender']
		else:
			graph.node[X]['gender']= "None"
	
		# Check friendships with the other members of the group:		
		# Creating requests
		all_requests = []
		for j,m in enumerate(users):
			single_request= {'method':'GET', 'relative_url': k['id']+'/friends/'+m['id']}
			all_requests.append(single_request)
		
	# Making batch requests
	# https://developers.facebook.com/docs/graph-api/making-multiple-requests/
	# Split the list of requests in blocks of 50 requests, the limit for batch requests
	chunks = split_seq(all_requests, 50)
	
	for u in chunks:
		batch_request = json.dumps(u)			
		try:
			facebook_request = requests.post(end_point, params={'access_token': INFINITE_TOKEN, 'batch': batch_request})
			#result_string = json.loads(facebook_request.text.strip("'<>() ").replace('\'', '\"'))
		except: 
			print ""
			print "There was an error. Waiting 30 minutes before starting again..."
			sleep(60*30)
			facebook_request = requests.post(end_point, params={'access_token': INFINITE_TOKEN, 'batch': batch_request})
		try:
			result_string = json.loads(facebook_request.text)
		except:
			print "There was an error n decoding the JSON data"
			result_string = "error"

		if "error" in result_string:
                	# Wait 30 minutes if we reach the user limit
                        # See https://developers.facebook.com/docs/reference/ads-api/api-rate-limiting/
                        print ""
			print "There was an error. Waiting 30 minutes before starting again..."
                        sleep(60*30)

                        facebook_request = requests.post(end_point, params={'access_token': INFINITE_TOKEN, 'batch': batch_request})
                        result_string = json.loads(facebook_request.text)

		for z in result_string:
			if z is not None and z["body"] is not None:
				result_dict = json.loads(z["body"])
				# Debug
				# print result_dict
				if "data" in result_dict and len(result_dict["data"]) != 0:
					for t in result_dict["data"]:
						Y = t["name"].encode("utf-8")
						print "- Friend with",Y
						graph.add_edge(X,Y)
			
# Save the file and exit	
print ""
print "The group was analyzed succesfully."
print ""
print "Saving the file as "+group+"-friendships.gexf..."
nx.write_gexf(graph,group+"-friendships.gexf")