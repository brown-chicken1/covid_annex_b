# covid_annex_b
Command line program which scrapes and does (very) basic analytics on dormitory COVID cases as published in Singapore Ministry of Health's Annex B press release

The Singapore Ministry of Health publishes data on COVID-19 infection rates amongst dormitory residents daily; it is part of the press release and is located in Annex B.

This program was my first attempt at a program; it still runs from the command line for now but I hope to integrate it into a web interface in future, as part of CS50's Final Project.
The program scrapes every press release released by MOH where Annex Bs are published, downloads them and compiles the total case number, and daily case increase, for every cluster,
every day.

There are 3 files, 

1. 'urls-collecting.py' scrapes the MOH website for the applicable press releases (that have links to Annex Bs) and puts them in to a .csv file called urls.csv.
2. 'pdf-downloading.py' uses the urls.csv file and downloads all the Annex Bs from the links listed in the csv file.
3. 'analysis.py' does the bulk of the work, by scraping the pdf files, storing everything for analysis. Analysis.py has 4 functions:
    a. one can search the file with keywords and the program will return clusters that match the keywords. The search results can be used to plot graphs of new cases against time.
    b. one can plot the graphs of new covid cases against time, for a maximum of 5 clusters.
    c. one can select a timeframe, and the program returns the top 5 clusters in terms of number of new cases within the timeframe
    d. one can make a wordcloud of the case clusters.
    
As mentioned, this is an elementary attempt so code might not be perfect, I have taken care to include as many comments as possible and make it easier to read. 
Appreciate feedback and advice, especially on the scraping portion. One difficulty I encountered was the non standardisation of the way cases were listed - some were missing
brackets in some entries, or had other formatting errors. This led to a few irregularities in the generation of the data, but I hope to get advice on how this could be improved in future.
