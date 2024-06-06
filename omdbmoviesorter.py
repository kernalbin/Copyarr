import requests
import json
import os
import re
import shutil
import subprocess

src = "/data/0/movies"
data = "/data/0/util/Copyarr/omdbjson"
omdbapikey = "e5059e31"


def collect_omdb(src, data):
    imdb_ids = []

    # Get list of imdb id's from movie files
    dirs = os.listdir(src)
    for dir in dirs:
        path = src+"/"+dir
        if (os.path.isdir(path)):
            files = os.listdir(path)
            for file in files:
                if("imdb-" in file):
                    result = re.search(r".imdb-(tt\d*).", file)
                    imdb_ids.append(result.group(1))
                    break

    print("Found " + str(len(imdb_ids)) + " movies")

    # Remove id's of items already pulled from omdb
    for dir in os.listdir(data):
        if dir in imdb_ids:
            imdb_ids.remove(dir)

    print(str(len(imdb_ids)) + " movies missing data")
    input("Continue?")

    # Grab omdb data and store in file
    for id in imdb_ids:
        print("Requesting: " + id)
        r = requests.get('http://www.omdbapi.com/?apikey=' + omdbapikey + '&i=' + id + "&plot=full")
        rjson = json.loads(r.text)
        if (rjson["Response"] == "True"):
            with open(data+"/"+id, 'w') as f:
                f.write(r.text)
        else:
            print("Failed to get data for: " + id)

def get_ids(data):
    return os.listdir(data)

def get_json(data, id):
    if (id in os.listdir(data)):
        with open(data + "/" + id, 'r') as f:
            return json.loads(f.readline()) 
    else:
        return json.loads("{}")

def is_float(element: any) -> bool:
    #If you expect None to be passed:
    if element is None: 
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False

def get_movies_filtered(ids: list, data: str, attribute: str, comp: str, value: str) -> list:
    f_ids = []
    for id in ids:
        idjson = get_json(data, id)
        if (attribute == "YEAR"):                                                             # YEAR - filter by year
            if (comp == "="):
                if (not is_float(idjson["Year"])):
                    continue
                if (int(idjson["Year"]) == int(value)):
                    f_ids.append(id)
            elif (comp == ">"):
                if (not is_float(idjson["Year"])):
                    continue
                if (int(idjson["Year"]) > int(value)):
                    f_ids.append(id)
            elif (comp == "<"):
                if (not is_float(idjson["Year"])):
                    continue
                if (int(idjson["Year"]) < int(value)):
                    f_ids.append(id)
        elif (attribute == "IMDB"):                                                           # IMDB - filter by imdb rating
            if (comp == "="):
                if (not is_float(idjson["imdbRating"])):
                    continue
                if (float(idjson["imdbRating"]) == float(value)):
                    f_ids.append(id)
            elif (comp == ">"):
                if (not is_float(idjson["imdbRating"])):
                    continue
                if (float(idjson["imdbRating"]) > float(value)):
                    f_ids.append(id)
            elif (comp == "<"):
                if (not is_float(idjson["imdbRating"])):
                    continue
                if (float(idjson["imdbRating"]) < float(value)):
                    f_ids.append(id)
        elif (attribute == "IMDBVOTE"):                                                       # IMDBVOTE - filter by imdb votes
            if (comp == "="):
                if (not is_float(idjson["imdbVotes"])):
                    continue
                if (int(idjson["imdbVotes"]) == int(value)):
                    f_ids.append(id)
            elif (comp == ">"):
                if (not is_float(idjson["imdbVotes"])):
                    continue
                if (int(idjson["imdbVotes"]) > int(value)):
                    f_ids.append(id)
            elif (comp == "<"):
                if (not is_float(idjson["imdbVotes"])):
                    continue
                if (int(idjson["imdbVotes"]) < int(value)):
                    f_ids.append(id)
        elif (attribute == "META"):                                                           # META - filter by metascore
            if (comp == "="):
                if (not is_float(idjson["Metascore"])):
                    continue
                if (float(idjson["Metascore"]) == float(value)):
                    f_ids.append(id)
            elif (comp == ">"):
                if (not is_float(idjson["Metascore"])):
                    continue
                if (float(idjson["Metascore"]) > float(value)):
                    f_ids.append(id)
            elif (comp == "<"):
                if (not is_float(idjson["Metascore"])):
                    continue
                if (float(idjson["Metascore"]) < float(value)):
                    f_ids.append(id)
        elif (attribute == "RATED"):                                                          # RATED - filter by rating
            if (comp in idjson["Rated"]):
                f_ids.append(id)
        elif (attribute == "GENRE"):                                                          # GENRE - filter by genre
            if (comp in idjson["Genre"]):
                f_ids.append(id)
        elif (attribute == "LANG"):                                                           # LANG - filter by language
            if (comp in idjson["Language"]):
                f_ids.append(id)
    return f_ids

def get_movies_path(src, ids) -> dict:
    movie_dict = {}
    dirs = os.listdir(src)
    for dir in dirs:
        path = src+"/"+dir
        if (os.path.isdir(path)):
            files = os.listdir(path)
            for file in files:
                if("imdb-" in file):
                    result = re.search(r".imdb-(tt\d*).", file)
                    if (result.group(1) in ids):
                        movie_dict[result.group(1)] = path
                        break
    return movie_dict

def get_folder_size(path) -> int:
    size = 0
    for path, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(path, f)
            try:
                size += os.path.getsize(fp)
            except OSError:
                print(fp + " error, ignoring")
                pass
    return size

def byte_to_gig(num: int) -> int:
    return int(num / 1000000000)

collect_omdb(src, data)
ids = get_ids(data)
filtered_ids = []

proceed = False
while(not proceed):
    print("")
    total_ids = str(len(ids))
    total_filtered = str(len(filtered_ids))
    q = input(total_filtered + "/" + total_ids + ">")
    qsep = q.split(" ")
    try:
        qsep[3]
    except IndexError:
        qsep.append(0)

    if (qsep[0] == "help"):
        print("options:")
        print("help     | show help")
        print("list     | 'selected' or 'all'")
        print("add      | YEAR, IMDB, META, IMDBVOTE (<=>) (Value)")
        print("add      | RATED, GENRE, LANG (Value)")
        print("remove   | YEAR, IMDB, META, IMDBVOTE (<=>) (Value)")
        print("remove   | RATED, GENRE, LANG (Value)")
        print("size     | get size of selected movies")
        print("copy     | (destination) copy movies to destination")
        print("rsync    | (destination) uses rsync to copy faster, linux only")
        print("path     | print out selected movies path(s)")
        print("quit     | exit program")

    elif (qsep[0] == "list"):                                                               # LIST - Selected or All Movies
        if (qsep[1] == "selected"):
            for id in filtered_ids:
                print(get_json(data, id)["Title"])
        elif (qsep[1] == "all"):
            for id in ids:
                print(get_json(data, id)["Title"])

    elif (qsep[0] == "add"):                                                                # ADD - filter movies
        new_additions = get_movies_filtered(ids, data, qsep[1], qsep[2], qsep[3])

        print(str(len(new_additions)) + " movies meet filter")
        if (len(new_additions) > 0):
            while (True):
                q2 = input("confirm / cancel / list > ")
                if (q2 == "confirm"):
                    [filtered_ids.append(x) for x in new_additions if x not in filtered_ids]
                    break
                elif (q2 == "cancel"):
                    break
                elif (q2 == "list"):
                    for id in new_additions:
                        print(get_json(data, id)["Title"])

    elif (qsep[0] == "remove"):                                                             # REMOVE - filter movies
        to_remove = get_movies_filtered(filtered_ids, data, qsep[1], qsep[2], qsep[3])              

        print(str(len(to_remove)) + " movies meet filter")
        if (len(to_remove) > 0):
            while (True):
                q2 = input("confirm / cancel / list >")
                if (q2 == "confirm"):
                    filtered_ids = [i for i in filtered_ids if i not in to_remove]
                    break
                elif (q2 == "cancel"):
                    break
                elif (q2 == "list"):
                    for id in to_remove:
                        print(get_json(data, id)["Title"])

    elif (qsep[0] == "size"):
        total_size = 0
        for id, path in get_movies_path(src, filtered_ids).items():
            total_size += get_folder_size(path)
        print(str(byte_to_gig(total_size)) + "GB")

    elif (qsep[0] == "copy"):
        dest = qsep[1]
        
        print("Ready to move " + str(len(filtered_ids)) + " movies")
        print("From: " + src)
        print("To: " + dest)
        total_size = 0
        for id, path in get_movies_path(src, filtered_ids).items():
            total_size += get_folder_size(path)
        print("Total size: " + str(byte_to_gig(total_size)) + "GB")
        input("Continue?")

        total_copied = 0
        for id, path in get_movies_path(src, filtered_ids).items():
            print("Copied " + str(total_copied) + " / " + str(len(filtered_ids)))
            dest_path = dest + "/" + path.split("/")[-1]
            shutil.copytree(path, dest_path)
            total_copied += 1

    elif (qsep[0] == "rsync"):
        dest = qsep[1]

        if (not os.path.isdir(dest)):
            os.mkdir(dest)
        
        print("Ready to move " + str(len(filtered_ids)) + " movies")
        print("From: " + src)
        print("To: " + dest)
        total_size = 0
        for id, path in get_movies_path(src, filtered_ids).items():
            total_size += get_folder_size(path)
        print("Total size: " + str(byte_to_gig(total_size)) + "GB")
        input("Continue?")

        total_copied = 0
        for id, path in get_movies_path(src, filtered_ids).items():
            print("Copied " + str(total_copied) + " / " + str(len(filtered_ids)))
            subprocess.call(["rsync", "-aW", "--no-i-r", "--info=progress2", "--info=name0", path, dest])
            total_copied += 1

    elif (qsep[0] == "path"):
        print(get_movies_path(src, filtered_ids))

    elif (qsep[0] == "quit"):
        proceed = True