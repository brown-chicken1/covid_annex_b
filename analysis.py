import fitz
import re
import unidecode
import datetime
import csv

from matplotlib import pyplot as plt
from wordcloud import WordCloud

def replace_with_numbers(to_be_replaced):

    # in the press releases, numbers 10 or below are in words so we change them to numbers
    # for easier analysis

    word_to_number = {"one": "1",
                      "two": "2",
                      "three": "3",
                      "four": "4",
                      "five": "5",
                      "six": "6",
                      "seven": "7",
                      "eight": "8",
                      "nine": "9",
                      "ten": "10"
                      }

    if word_to_number.get(to_be_replaced.lower()):
        return word_to_number.get(to_be_replaced.lower())

    return to_be_replaced


def clusters():

    # as the files are arranged in sequential format, the number of press releases in total =
    # the number of files that the program reads
    number_of_releases = int(input("Please enter the number of press releases in total: "))

    # first 2 elements of the case
    table_heading = ["Name", "Total"]

    date = datetime.date(2020, 4, 19)
    # first instance of Annex B was reported on 20/4/20

    # creating table headings
    for i in range(number_of_releases):
        date += datetime.timedelta(1)
        table_heading.append(date)

    # creating empty list which will become basis for the clusters
    cluster_data = [table_heading]
    opening(cluster_data, number_of_releases)


def opening(cluster_data, number_of_releases):

    for i in range(number_of_releases):

        # create a list to store all the locations for later use (word-cloud, indexing etc)
        location_data = [data[0] for data in cluster_data]
        filename = 'Annex B' + str(i) + '.pdf'
        doc = fitz.open(filename)

        # searching a page
        for page in doc:
            # tried "Blocks" but it wouldn't detect the newline characters sometimes and everything would be
            # in a huge blob (not standardised)
            lines = page.getText("text")

            # just to make sure i didn't miss out any characters that were somehow not in unicode
            lines = unidecode.unidecode(lines)

            # remove newline characters and split into list by fullstop (End of a "New cluster" sentence)
            lines = lines.replace('\n', '')
            lines = lines.split('.')

            # removes the numbering, roman numerals shouldn't be longer than 15 chars
            lines = [line.strip() for line in lines if not len(line) < 15]

            for line in lines:

                # if new cluster and not seen before in the press release
                if re.search("a new cluster at", line):
                    try:
                        location = re.search('at [A-Z0-9][a-zA-Z0-9_()\-@&/# ]+.', line).group().lstrip('at ').rstrip('.').strip()

                    # capture weird occurrences of stuff above not fully eliminating the wrong sentences
                    except AttributeError:
                        pass

                    # first word of the sentence is dedicated to new cases
                    new_cases = int(replace_with_numbers(line.split(' ')[0]))
                    # sometimes, they link to earlier cases confirmed before so i added that in as well
                    earlier_cases = re.search(' [a-z]+ previous case', line)

                    # create a list to put the details of new clusters, and the location
                    new_cluster = []
                    new_cluster.append(location)

                    # if indeed the new cases had been linked to previous cases
                    if earlier_cases:
                        earlier_cases = int(replace_with_numbers(earlier_cases.group().replace('previous case', '').strip()))
                        new_cases = new_cases + earlier_cases

                    # add to the cluster (TOTAL cases)
                    new_cluster.append(new_cases)

                    # fill up the preceding columns for the dates that had already passed while the cluster didn't exist
                    days_without_cases = [0] * i
                    new_cluster.extend(days_without_cases)

                    # add to the cluster (new cases on the confirmed date)
                    new_cluster.append(new_cases)
                    cluster_data.append(new_cluster)

                elif re.search("which has a total ", line):

                    # find location matches using Regex, inclusive of special characters an
                    location = re.search('at t?h?e? ?a? ?[A-Z0-9][a-zA-Z0-9_()\-@&/# ]+,', line).group()
                    location = re.sub("at ", "", location).rstrip(',').strip()

                    # replace words with numbers, convert the comma for 4-digit cases away
                    new_cases = int(replace_with_numbers(line.split(' ')[0]).replace(',', ''))
                    try:
                        total_cases = int(replace_with_numbers(line.split(' ')[-4]).replace(',', ''))
                    except ValueError:
                        try:
                            total_cases = int(replace_with_numbers(line.split(' ')[-3]).replace(',', ''))
                        except ValueError:
                            # other errors (one of the strings was missing a full stop. but no idea how to fix that.
                            # didn't affect the results in the end)
                            print("Meow meow")


                    # if cluster already exists, then we update the cluster
                    if location in location_data:
                        cluster_index = location_data.index(location)
                        cluster_data[cluster_index].append(new_cases)
                        cluster_data[cluster_index][1] = cluster_data[cluster_index][1] + new_cases
                    else: # create an entry for new cluster (new cluster but the number doesn't start from 0, because
                          # of format issues - cluster already existed before Annexes B were being published

                        new_cluster = []
                        new_cluster.append(location)
                        new_cluster.append(total_cases)

                        days_without_cases = [0] * i
                        new_cluster.extend(days_without_cases)
                        new_cluster.append(total_cases)
                        cluster_data.append(new_cluster)

        # if the cluster doesn't show up in the press release,
        for cluster in cluster_data:
            try:
                cluster[1 + i + 1]

            # we take it that there's 0 cases, and append accordingly
            except IndexError:
                cluster.append(0)

    selection = input("What do you want to do? (Input numbers)\n1. Search\n2. Plot\n3. Rank\n4. Word Cloud")

    while True:
        if selection == "1":
            search_cluster(cluster_data, location_data, number_of_releases)

        elif selection == "2":
            plot_graph(cluster_data, location_data, number_of_releases)

        elif selection == "3":
            rank_cases(cluster_data, location_data)

        elif selection == "4":
            word_cloud(location_data)
        else:
            print("Option is invalid.")

        again = input("Play again? Y/N")
        if again.lower() == "n":
            break

        selection = input("What do you want to do? (Input numbers)\n1. Search\n2. Plot\n3. Rank\n4. Word Cloud")

def search_cluster(cluster_data, location_data, number_of_releases):

    clusters_found = []
    clusters_selected = []
    searching = 'y'
    select_from_results = 'Y'

    while searching.lower() == 'y':
        counter = 0
        keywords = input("Please enter words: ")

        # searching for the cluster
        for data in cluster_data:
            if keywords.lower() in data[0].lower():
                clusters_found.append(data[0])      # adds it to the list of locations found
                print(f"{counter + 1}: {data[0]}")  # prints it out for user input
                counter += 1

        print(f"There are {counter} clusters total.")

        while select_from_results.lower() == "y":   # add
            intention = input("Select? (Indicate N if not selecting, otherwise select by number)")

            if intention.lower() == 'n': # if they don't want to continue
                break

            try: # selecting results
                clusters_selected.append(clusters_found[int(intention) - 1])
            except IndexError:
                print("Try again, value exceeds number of results")

            select_from_results = input("Enter some more? Y for Yes, any key for No.")

        select_from_results = 'Y'
        searching = input("Search again? Y for Yes, any key for No.")
        clusters_found = []

    plotting = input("Plot a graph? Y for Yes, any key for No. If more than 5 locations were selected, only first 5 will be used.")
    if plotting == 'y':
        if len(clusters_selected) > 5:
            clusters_selected = clusters_selected[:5]
        plot_graph(cluster_data, location_data, number_of_releases, clusters_selected)

# rank clusters based on case number, in a given date interval
def rank_cases(cluster_data, location_data):

    location_data = location_data[1:]
    # first date
    month = input("Enter starting month: ")
    day = input("Enter starting day: ")
    chosen_start_date = datetime.date(2020, int(month), int(day))
    chosen_start_index = cluster_data[0].index(chosen_start_date) # we match the date given, to the index in the cluster_data list

    # second date
    month = input("Enter ending month: ")
    day = input("Enter ending day: ")
    chosen_end_date = datetime.date(2020, int(month), int(day))
    chosen_end_index = cluster_data[0].index(chosen_end_date) + 1


    # search for case count within the given dates
    case_count = [sum(data[chosen_start_index:chosen_end_index]) for data in cluster_data[1:]]

    # put into a dictionary
    case_dict = dict(zip(location_data, case_count))

    rank_max_cases(case_dict, 0)


def rank_max_cases(case_dict, i):

    # for recursive purposes
    if i == 5:
        print("That is all.")
    else:
        temp = case_dict.copy()

        rankings = ['highest', 'second-highest', 'third-highest', 'fourth-heighest', 'fifth-heighest']
        top_cases = [-1, [0]]
        while temp:                                 # referenced from https://stackoverflow.com/questions/9853302/using-pythons-max-to-return-two-equally-large-values
            key, value = temp.popitem()                     # (This takes into account situations where the case might have more than 1 location)
            if int(value) > top_cases[0]:
                top_cases = [value, [key]]
            elif int(value) == top_cases[0]:
                top_cases[1].append(key)

        # if there's only 1 location with that case number
        if len(top_cases[1]) == 1:
            print(f"{top_cases[1][0]} has the {rankings[i]} number of cases, where {top_cases[0]} cases were found between the intervals stated.")

        # if the case number has more than 1 location corresponding to it
        else:
            print(f"There are multiple locations with the{rankings[i]} number of cases, which are: ")
            for cases in top_cases[1]:
                print(f" - {cases}")
            print(f"and they have {top_cases[0]} cases in total.")

        # remove the locations concerned, from the dictionary
        case_dict = {k:v for k,v in case_dict.items() if v != top_cases[0]}

        i += 1
        # call function again until 5 times
        rank_max_cases(case_dict, i)


def plot_graph(cluster_data, location_data, number_of_releases, clusters_selected = None):
    print("You can plot a maximum of 5 graphs.")
    clusters_to_plot = []

    graph_colours = ['g', 'r', 'b', 'k', 'm']

    for i in range(5):

        broken = False

        while True:
            # if it wasn't passed from the first searching option
            if clusters_selected == None:
                x = input(f"Please enter cluster {i + 1} (Indicate 0 if not interested): ")
            else:
                try:
                    x = clusters_selected[i]
                except IndexError:
                    break

            # if it's a valid option
            if x in location_data:
                # since the index of the location in cluster_index is the same as the index of the location in location_index
                cluster_index = location_data.index(x)

                clusters_to_plot.append(x)
                plt.plot(cluster_data[0][2:], cluster_data[cluster_index][2:], graph_colours[i], label = cluster_data[cluster_index][0:2])

                break

            # to stop asking for new locations
            elif x == '0':
                print("Okay")
                broken = True
                break

            print("Error, please enter valid cluster")

        # exits out of loop and plots the graph
        if broken == True:
            break

    plt.legend(loc = 9)
    plt.xlabel("Number of days")
    plt.xticks(rotation = 45)

    plt.ylabel("Dates")
    plt.show()


def word_cloud(location_data):

    cleaned_addresses = []

    # list of prefix and suffixes to remove from the word cloud so they don't interfere with the actual street names
    with open("road_prefix_and_suffix.csv", "r") as file:
        reader = csv.reader(file)
        types_of_roads = [data[0] for data in reader]

    for data in location_data:
        data = re.sub('\d+[A-Za-z]?', '', data) # remove numbers and alphabets after numbers

        for types in types_of_roads:
            if types in data:
                cleaned_addresses.append(data.replace(types, ''))

    # put into a string for wordcloud to work- referenced from https://www.datacamp.com/community/tutorials/wordcloud-python
    cleaned_addresses = ' '.join(address for address in cleaned_addresses)

    wordcloud = WordCloud(stopwords=types_of_roads, background_color="white").generate(cleaned_addresses)

    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()

clusters()

