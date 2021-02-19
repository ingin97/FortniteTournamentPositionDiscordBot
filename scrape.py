from contextlib import closing
from selenium import webdriver
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
from request import simple_get
import re
import random
import math
import sys

url = ""
urlDefault = "https://fortnitetracker.com/events/epicgames_S13_FNCS_EU_Qualifier4_PC?window=S13_FNCS_EU_Qualifier4_PC_Round1&page="

numberOfPages = 100
driver = None
FOUND = False
response = ""

def main(arguments):
  global url
  global driver
  driver = setup()

  if len(arguments) == 1:
    manual()
  elif len(arguments) == 4:
    url = arguments[1]
    nick = arguments[2]
    score = int(arguments[3])
    page = 0
    if score > -1:
      page = findWithBinarySearch(score, nick)
    if not FOUND: findWithIncrement(page, nick)
  
  return response

def manual():
  quit = None
  print("Hello and welcome to this helpful machine.")
  print("Today I can give you your rank and page number for a specified tournament on FortniteTracker.com.")
  print("Just type in the url for the tournament, your epic name and the score you are currently at.")
  global url
  url = input("Url for the tournament: ")
  if url == "": 
    url = urlDefault
  while quit != "yes" or quit != "y" or quit != "Yes":
    nick = input("Nick: ")
    score = int(input("Score: "))
    page = 0
    if score > -1:
      page = findWithBinarySearch(score, nick)
    if not FOUND: findWithIncrement(page, nick)
    quit = input("Do you want to quit?")

def findWithIncrement(startPage, nick):
  page = startPage
  found = False
  while not found:
    print("Page number: ", str(page))
    soup = getSoup(page)
    for i in range(100):
      raw_data = soup.find(id="row" + str(i))
      data = getRowData(raw_data)

      # If found correct nick
      if (data["players"].find(nick) != -1):
        printRow(raw_data)
        print("Found on page number: ", str(page))
        found = True
        break
    if (page == 99):
      print("Could not find you in this tournament.")
      break
    page += 1


def findWithBinarySearch(score, nick):
  global FOUND
  L = 0
  R = numberOfPages - 1
  lastPage = -1
  page = -1

  # Find a page with the correct score
  while L<=R:
    page = math.floor((L+R)/2)
    print("Page number: ", str(page))
    if page == lastPage: break
    lastPage = page
    soup = getSoup(page)

    _max = getRowData(soup.find(id="row" + str(0)))["points"]
    _min = getRowData(soup.find(id="row" + str(99)))["points"]
    # print("score: ", str(score), "_max: ", str(_max), "_min: ", str(_min))
    if (score > _max): 
      R = page - 1
      continue
    if (score < _min): 
      L = page + 1
      continue
  
  # Decrement until we are sure we do not miss any pages
  while True:
    print("Page number: ", str(page))
    soup = getSoup(page)

    for i in range(100):
      raw_data = soup.find(id="row" + str(i))
      data = getRowData(raw_data)

      # If found correct nick
      if (data["players"].find(nick) != -1):
        printRow(raw_data)
        print("Found on page number: ", str(page))
        FOUND = True
        return page
    _max = getRowData(soup.find(id="row" + str(0)))["points"]
    if (score < _max): 
      break
    page -= 1

  # Increment until we find the correct page
  page = lastPage + 1
  while True:
    print("Page number: ", str(page))
    soup = getSoup(page)
    
    for i in range(100):
      raw_data = soup.find(id="row" + str(i))
      data = getRowData(raw_data)

      # If found correct nick
      if (data["players"].find(nick) != -1):
        printRow(raw_data)
        print("Found on page number: ", str(page))
        FOUND = True
        return page

    _min = getRowData(soup.find(id="row" + str(99)))["points"]
    if (score > _min): 
      print("Could not find you with this score in this tournament.")
      break
    if (page == 99):
      print("Could not find you in the top 10'000.")
      break
    page += 1
  return page
  
def getSoup(page):
  driver.get(url + str(page))
  raw_html=driver.page_source
  return BeautifulSoup(raw_html, "html.parser")

def getRowData(raw_data):
  img = raw_data.findAll("img")
  nationality = ""
  for tag in img:
    nationality += tag['title'] + " "
  
  data = raw_data.text.split()
  rank = int(data[0])
  players = " ".join(data[1:-5])
  points = int(data[-5])

  return {"rank":rank, "nationality":nationality, "players":players, "points":points}

# Print the rows in a fine manner
def printRow(raw_data):
  data = getRowData(raw_data)
  rank = "Rank: " + str(data["rank"])
  nationality = "| Nationality: " + data["nationality"]
  players = "| Players: " + data["players"]
  points = "| Points: " + str(data["points"])
  print("----------------------------")
  print(rank, nationality, players, points)
  global response
  response = rank + nationality + players + points

# Used to make the site load properly.
def setup():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument('log-level=3')
    return webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)

if __name__ == '__main__':
    main(sys.argv)
    