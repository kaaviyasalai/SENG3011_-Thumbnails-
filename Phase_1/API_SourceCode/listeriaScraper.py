# INSTALL BEAUTIFULSOUP
# pip install beautifulsoup4
# pip install pymongo

from functools import partialmethod
from bs4 import BeautifulSoup
import requests
import re
import json
from datetime import datetime
from pymongo import MongoClient


#check if url exists in json list
def check_url(url, list):
    for article in list:
        if (article["url"] == url):
            return 1
    return 0


def listeria_scraper():
    #base of the cdc url
    base = "https://www.cdc.gov"

    #go to the first listeria page
    page = requests.get("https://www.cdc.gov/listeria/outbreaks/packaged-salad-mix-12-21/index.html")
    soup = BeautifulSoup(page.content, 'html.parser')

    #load the disease and syndrome lists
    #diseaseFile = open('diseaseList.json')
    # if the above line causes error try the line below
    diseaseFile = open('Phase_1\API_SourceCode\diseaseList.json')
    diseaseList = json.load(diseaseFile)

    #syndromeFile = open('syndromeList.json')
    # if the above line causes error try the line below
    syndromeFile = open('Phase_1\API_SourceCode\syndromeList.json')
    syndromeList = json.load(syndromeFile)

    #regex pattern for the index files and files with case numbers
    patternIndex = re.compile("/listeria/outbreaks/.+/index.html")
    patternLocation = re.compile("/listeria/outbreaks/.+/map.html")

    #intialise data structures
    articlesData =[]

    #first find all the links in the base page
    for link in soup.find_all('a'):

        #initialise data structures
        objects = { "diseases": [], "syndromes": [], "event_date": "", "locations": [], }
        data = { "url": "", "date_of_publication": "", "headline": "", "main_text": "", "reports": [] }
        #data["reports"] = objects
        locations = []

        #add listeriosis as default
        diseases = ["listeriosis"]
        syndromes = []

        #get different outbreak links
        if (patternIndex.match(str(link.get('href')))):
            route = str(link.get('href'))

            #now navigate to individual outbreak pages
            p = requests.get(base + route)
            s = BeautifulSoup(p.content, 'html.parser')

            #check current url is not already added to articlesData
            if (check_url((base + str(link.get('href'))), articlesData)):
                continue

            #add url to articlesData
            data["url"] = base + str(link.get('href'))

            #find the date of publication
            for para in s.find_all('p'):
                if (str(para)).startswith("<p>Posted"):
                    d = str(para)

                    #remove excess tags and junk
                    d = d.replace("<p>Posted ", "")
                    d = d.replace("<p>Posted ", "")
                    d = d.replace("</p>", "")
                    d = d.replace("at ", "")
                    d = d.replace("ET", "")
                    d = d.strip()
                    try:
                        #convert data type from 'march 8, 2022'
                        newDate = datetime.strptime(d,"%B %d, %Y")

                        #add the date of publication
                        data["date_of_publication"] = str(newDate.strftime('%Y-%m-%d xx:xx:xx'))
                    except ValueError:
                        try:
                            #convert data type from 'June 10, 2015 10:30 AM'
                            newDate = datetime.strptime(d,"%B %d, %Y %I:%M %p")
                            data["date_of_publication"] = str(newDate.strftime('%Y-%m-%d %H:%M:xx'))
                        except ValueError:
                            #no match; set to empty string
                            #year is mandatory?
                            data["date_of_publication"] = 'xx-xx-xx xx:xx:xx'

                #check if any other diseases are mentioned in the page

                #print(objects["diseases"])
                for disease in diseaseList:
                    if ((str(para)).find(disease["name"]) != -1) and (disease["name"] not in diseases):
                        diseases.append(disease["name"])

                #check if any syndromes are mentioned in the page
                for syndrome in syndromeList:
                    if (str(para)).find(syndrome["name"]) != -1 and (syndrome["name"] not in syndromes):
                        syndromes.append(syndrome["name"])

            #find the headline
            #remove tags and junk
            headline = str(s.title)
            headline = headline.replace("<title>", "")
            headline = headline.replace("</title>", "")
            try:
                headlines = headline.split('|')
                data["headline"] = headlines[0]
            except:
                None
                data["headline"] = headline


            ##############   finding the main text




            ################## finding the event date




            #find the locations
            route = str(link.get('href'))
            route = route.replace("index.html", "map.html")

            #now navigate to individual pages that end in map.html
            p = requests.get(base + route)
            s = BeautifulSoup(p.content, 'html.parser')

            for t in s.find_all('td'):
                patternState = re.compile("^(<td|<td>)[^State][^Case Count][^0-9]+</td>")
                if (patternState.match(str(t))):
                    state = str(t)
                    state = state.replace("<td>", "")
                    state = state.replace("</td>", "")
                    state = state.replace("State", "")
                    state = state.replace("<strong>Total</strong>", "")
                    state = state.replace("<p>", "")
                    state = state.replace("</p>", "")
                    state = state.replace('<td class="row">', "")
                    state = state.replace("<strong>Total ill persons</strong>", "")
                    state = state.replace("\n", "")
                    if state not in locations and state != "":
                        locations.append(state)

                #if locations is empty then 
                #DONT KNOW HOW TO PARSE COLLAPSABLE TABLES :(
                #if (locations == []):
                #print("empt")


            objects["locations"] = locations
            objects["syndromes"] = syndromes
            objects["diseases"] = diseases
            data["reports"] = objects
            articlesData.append(data)

    return articlesData

#takes a while to print
if __name__ == "__main__":

    cluster = "mongodb+srv://thumbnails:thumbnails@cluster0.lfkm3.mongodb.net/SENG3011?retryWrites=true&w=majority"
    client = MongoClient(cluster)

    # Select the database and the cluster 
    db = client.SENG3011
    collection = db.SENG3011_collection

    # Delete all entries in the cluster
    result = collection.delete_many({})

    listeria_scraper()
    for i in listeria_scraper():
        print(i)
        print("\n")
        # Add document to the cluster
        result = collection.insert_one(i) 

'''
url - done
date of pub- done
headline - done
main_text -

reports:
    diseases - done
    syndromes - done
    event_date
    locations
'''
