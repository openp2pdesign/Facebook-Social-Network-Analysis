# coding: utf-8
#
# Social Network Analysis of a Facebook group interactions
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

graph=nx.DiGraph()
comments = {}
comments[0]={0:""}
i = 0
newpage = {}

# Some group examples:
# Fabber in Italia
fii = "192759480789364"
# Fab9
fab9 = "152023668302761"

group = fab9
base_url = 'https://graph.facebook.com/'+group+'/feed'

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

oauth_url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % \
    (client_id, client_secret, ACCESS_TOKEN,)
message = requests.get(oauth_url)
message1 = message.content[13:]
INFINITE_TOKEN = message1[:message1.find("&expires=")]
print "The infinite token is:",INFINITE_TOKEN

# Then access Facebook with the infinite token
ACCES_TOKEN = INFINITE_TOKEN

# Get only the ID of the group users in order to get all of them
#fields = '&fields=id&limit=5000'
fields = ""
url = '%s?fields=%s&access_token=%s' % \
    (base_url, fields, ACCESS_TOKEN,)

# Interpret the response as JSON and convert back
# to Python data structures
print ""
print "Talking to the API..."
print ""
newpage[0] = requests.get(url).json()

# 
# Structure of the data in the Facebook Graph API
#
# For a post
# content["data"][1]
#
# Here's who posted it
# content["data"][1]["from"]["name"]
# content["data"][1]["from"]["id"]
#
# Here's who liked it
# content["data"][1]["likes"]["data"][0]["name"]
# content["data"][1]["likes"]["data"][0]["id"]
# 
# Here's who commented
# content["data"][1]["comments"]["data"][0]["from"]["name"]
# content["data"][1]["comments"]["data"][0]["from"]["id"]
# 
# From: http://stackoverflow.com/questions/16955653/facebook-graph-api-how-to-get-likes-for-comment
# In order to get who liked a comment:
# https://graph.facebook.com/POST_ID+"_"+COMMENT_ID?fields=likes
#
# likes_users["likes"]["data"][0]["name"]
#


#############################
print "INTERACTIONS ON A FACEBOOK GROUP"
print ""

while 1 > 0:
	print "-----------------------------------------"
	print "Reading page n.", i,"from the Facebook API..."
	print ""
	if i != 0:
		newpage[i] = requests.get(newpage[i-1]["paging"]["next"]).json()
	if "paging" in newpage[i].keys():
		
		for w,x in enumerate(newpage[i]["data"]):
		# Find the creator of the post
			creator_id = x["from"]["id"]
			creator_name = x["from"]["name"]
			print "---------------------------------"
			print "Post by:", creator_name
			comments[0]=creator_name
		
		# If there are likes, find who like the post and add an edge from them to the creator of the post
			if "likes" in x.keys():
				for y in x["likes"]["data"]:
					print "-Liked by", y["name"]
					print "Adding an edge between",y["name"],"and",creator_name
					graph.add_edge(y["name"],creator_name)
			else:
				pass
	
			# If there are comments...
			if "comments" in x.keys():
				# Add edges for each comment
				for k,y in enumerate(x["comments"]["data"]):
					print "----"
					print "Comment by:",y["from"]["name"]
					# Add an edge only towards the creator of the post (uncomment the following line and comment 
					# graph.add_edge(y["from"]["name"],creator_name)
					comments[k+1]=y["from"]["name"]
		
					# Add an edge for each like to a comment
					likes_url ='https://graph.facebook.com/'+x["id"]+"_"+y["id"]+"?fields=likes&access_token="+ACCESS_TOKEN
					likes_users = requests.get(likes_url).json()
					if "likes" in likes_users.keys():
						for k in likes_users["likes"]["data"]:
							print "-Liked by...",k["name"]
							graph.add_edge(k["name"],y["from"]["name"])
					else:
						pass
	
			# Adding edges from each commenter to her/his previous commenters and the post creator
			print "Adding edges for the comments..."
			for h in comments:
				if h > 0:
					print "- Commented by: ",comments[h]
					graph.add_edge(comments[h],creator_name)
					print "- Adding an edge from ",comments[h], "to", creator_name
					for l in comments:
						if l < h and l > 0:
							print "- Adding an edge from ",comments[h],"to",comments[l]
							graph.add_edge(comments[h],comments[l])
					print ""	
		
	else:
		print ""
		print "The group was analyzed succesfully."
		print ""
		print "Saving the file as "+group+"-interactions.gexf..."
		nx.write_gexf(graph, group+"-interactions.gexf")
		exit()
	
	i = i + 1
	