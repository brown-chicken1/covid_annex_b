from bs4 import BeautifulSoup
import requests
import unidecode
import re
import csv


def scrape():
    # scraping dates
    response = requests.get("https://www.moh.gov.sg/covid-19/past-updates")
    information = BeautifulSoup(response.text, "html.parser")

    urls = []
    # take into account differing values for the layouts in the website (found through trial & error
    # when scraping stopped prematurely)
    text_length = ["497", "479"]
    count = 0
    for length in text_length:

        press_releases = information.find_all("td", {"width": length})  # find all the text

        for stuff in press_releases:
            string = unidecode.unidecode(stuff.text).strip()

            count += 1

            # the last press release before the first Annex B was released - in other words scraping should stop here
            if string == '1,426 New Cases of COVID-19 Infection':
                broken = True
                break

            try:
                temp = stuff.find("a").attrs['href']
                # url to add to csv to scrape, question marks added to take into account non
                # standardisation of url format
                if re.findall(
                        "h?t?t?p?s?:?/?/?w?w?w?.?moh.gov.sg/news-highlights/details/1?\-?[0-9]{1,3}-more-cases-discharged-[0-9]?\-?[0-9]{1,3}-new-cases-of-covid-19-infection-confirmed",
                        temp):
                    urls.append(temp)

            except AttributeError:
                pass

        if broken == True:
            break

    # write to csv 
    with open("urls.csv", 'w', newline='') as file:

        writer = csv.writer(file)

        for url in urls:
            writer.writerow([url])

scrape()

