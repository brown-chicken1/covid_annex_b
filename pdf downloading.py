from bs4 import BeautifulSoup
import requests
import csv

def scrape():
    # scraping dates

    annex_c_compilation = []


    with open(r"urls.csv", "r") as file:
        reader = csv.reader(file)

        for website in reader:

            response = requests.get(website[0].strip())
            information = BeautifulSoup(response.text, "html.parser")

            date = information.find_all("h2")
            thing = information.find_all(href=True, sfref=True)

            for stuff in thing:
                if stuff.text.strip() == "Annex B":
                    annex_c_compilation.append(stuff.get('href'))
                    print(stuff.get('href'))


    save_pdf(annex_c_compilation)
    return annex_c_compilation

def save_pdf(annex_c_compilation):

    print("Begin file downloading...")

    for i in reversed(range(len(annex_c_compilation))):

        response = requests.get(annex_c_compilation[i].strip())


        with open('Annex B' + str(len(annex_c_compilation) - i - 1) + '.pdf', 'wb') as f:
            f.write(response.content)

scrape()



