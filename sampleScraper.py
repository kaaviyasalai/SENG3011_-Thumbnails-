# INSTALL BEAUTIFULSOUP
# pip install beautifulsoup4

from bs4 import BeautifulSoup
import requests


#go to the base page
page = requests.get("https://www.cdc.gov/listeria/outbreaks/packaged-salad-mix-12-21/index.html")
soup = BeautifulSoup(page.content, 'html.parser')

base = "https://www.cdc.gov/"


for link in soup.find_all('a'):

    #get different outbreak links
    if ((str(link.get('href'))).startswith("/listeria/outbreaks")) and (str(link.get('href')).endswith("/index.html")):
        route = str(link.get('href'))

        #now navigate to individual pages
        p = requests.get(base + route)
        s = BeautifulSoup(p.content, 'html.parser')

        #print the url
        print("Url: " + "base" + str(link.get('href')))

        #find the date of publication
        for para in s.find_all('p'):
            if (str(para)).startswith("<p>Posted"):
                print("Date of pub:" + str(para))

        #print the headline
        print("Headline: " + str(s.title))

        #finding the body??
        #hardcoded
        #print("diseases: Listeria")
        print("\n")
        #weird parsing of symptoms
        #go to subpage for location
