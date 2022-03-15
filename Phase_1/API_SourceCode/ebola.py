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


def ebola_scraper():

    url = "https://www.cdc.gov/vhf/ebola/outbreaks/drc/2018-may.html?CDC_AA_refVal=https%3A%2F%2Fwww.cdc.gov%2Fncezid%2Fdhcpp%2Febola-drc-2018.html"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    base = "https://www.cdc.gov"

    #load the disease and syndrome lists
    #diseaseFile = open('diseaseList.json')
    # if the above line causes error try the line below
    diseaseFile = open('Phase_1\API_SourceCode\diseaseList.json')
    diseaseList = json.load(diseaseFile)

    #syndromeFile = open('syndromeList.json')
    # if the above line causes error try the line below
    syndromeFile = open('Phase_1\API_SourceCode\syndromeList.json')
    syndromeList = json.load(syndromeFile)

    #intialise data structures
    articlesData =[]

    for link in soup.find_all('a'):
        #initialise data structures
        objects = { "diseases": [], "syndromes": [], "event_date": "", "locations": [], }
        data = { "url": "", "date_of_publication": "", "headline": "", "main_text": "", "reports": [] }
        locations = []

        #add ebola haemorrhagic fever as default
        diseases = ["ebola haemorrhagic fever"]
        syndromes = []
        
        if ((str(link.get('href'))).startswith("/vhf/ebola/outbreaks/drc/20")):
            route = str(link.get('href'))
            
            #now navigate to individual pages
            p = requests.get(base + route)
            s = BeautifulSoup(p.content, 'html.parser')

            #check current url is not already added to articlesData
            if (check_url((base + str(link.get('href'))), articlesData)):
                continue

            #add url to articlesData
            data["url"] = base + str(link.get('href'))

            #find the date of publication = last-reviewed-date
            #get rid of unnecessary tags
            pub_date = s.find("meta", property="cdc:last_reviewed")
            pub_date = str(pub_date).replace("<meta content=", "")                          #need to do str each time, or else date covertion wont work
            pub_date = str(pub_date).replace(' property="cdc:last_reviewed"/>', "")
            pub_date = str(pub_date).replace('"','')

            try:
                #convert data type from 'march 8, 2022'
                newDate = datetime.strptime(pub_date,"%B %d, %Y")
                data["date_of_publication"] = str(newDate.strftime('%Y-%m-%d xx:xx:xx'))
            except ValueError:
                #no match; set to empty string
                data["date_of_publication"] = 'xx-xx-xx xx:xx:xx'

            #check if any other diseases are mentioned in the page
            for p1 in s.find_all('p'):
                for disease in diseaseList:
                    if ((str(p1)).find(disease["name"]) != -1) and (disease["name"] not in diseases):
                        diseases.append(disease["name"])

                #check if any syndromes are mentioned in the page
                for syndrome in syndromeList:
                    if (str(p1)).find(syndrome["name"]) != -1 and (syndrome["name"] not in syndromes):
                        syndromes.append(syndrome["name"])

            #find the headline
            title = str(s.title)
            end_h = title.find(" | ")
            headline = title[7:end_h].strip()
            data["headline"] = headline

            #finding the main text
            main_text = ""
            event_date = ""
            heading_tags = ["h2", "h3", "h4"]
            for tags in s.find_all(heading_tags):
                if tags.text.strip() == "Overview":
                    for elem in tags.next_siblings:
                        if elem.name and elem.name.startswith('h'):
                            break
                        if elem.name == 'p':
                            main_text += elem.get_text()

            if main_text != "":                             #main text found
                data['main_text']= main_text

                #get event date
                end_date = main_text.find(" the")           #where published date ends
                event_date = main_text[3:end_date]          #get publish data, minus <p>On in beginning and everything after
                if event_date.endswith(','):                #some end with this, some don't
                    event_date = event_date[:-1]

                update_event = datetime.strptime(event_date,"%B %d, %Y")
                objects["event_date"] = str(update_event.strftime('%Y-%m-%d %H:%M:xx'))

            #remianing pages have main text under div cardholder
            if main_text == "":
                for paragraph in s.find_all('p'):
                    for elem in paragraph.next_siblings:
                        if elem.name and elem.name.startswith('h'):
                            break
                        if elem.name == 'p':  
                            main_text += elem.get_text()
            data['main_text']= main_text
            
            #get event date
            final_url = base + str(link.get('href'))
            if final_url == "https://www.cdc.gov/vhf/ebola/outbreaks/drc/2017-may.html":
                event_date = "May 11, 2017"
            elif final_url == "https://www.cdc.gov/vhf/ebola/outbreaks/drc/2014-august.html":
                event_date = "November 21, 2014"
            elif final_url == "https://www.cdc.gov/vhf/ebola/outbreaks/drc/2018-may.html":
                event_date = "May 8, 2018"
            else:
                end_date = main_text.find(" the")           #where published date ends
                event_date = main_text[3:end_date]          #get publish data, minus <p>On in beginning and everything after
                if event_date.endswith(','):                #some end with this, some don't
                    event_date = event_date[:-1]

            update_event = datetime.strptime(event_date,"%B %d, %Y")
            objects["event_date"] = str(update_event.strftime('%Y-%m-%d %H:%M:xx'))

            #find the locations
            if 'Eastern' in headline:
                star_pos = headline.find('Eastern')
            else:
                star_pos = headline.find('Democratic')

            curr_loc = headline[star_pos:]
            #print("Location: " + curr_loc)
            
            if curr_loc not in locations and curr_loc != "":
                locations.append(curr_loc)

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

    Delete all entries in the cluster
    result = collection.delete_many({})

    ebola_scraper()
    for i in ebola_scraper():
        print(i)
        print("\n")
        # Add document to the cluster
        #result = collection.insert_one(i) 

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
