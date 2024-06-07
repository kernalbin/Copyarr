import requests
import json
import os
import re
import shutil
import subprocess

# Parent folder containing movie files, in separate folders, file names must include imdb-{id}
src = "/data/0/movies"

# Location to store the omdb api data for each movie and the omdb api key
data_path = "/data/0/util/Copyarr/omdbjson"
omdbapikey = "e5059e31"

# Gets list of imdb id's from src folder containing movies with filenames containing the id's
# Finds any ids that don't already have data pulled
# Pulls the data for each remaining imdb id from omdb and stores them as files in data_path
def collect_omdb(src, data_path):
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
    for dir in os.listdir(data_path):
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
            with open(data_path+"/"+id, 'w') as f:
                f.write(r.text)
        else:
            print("Failed to get data for: " + id)

# Returns the json data from data_path for a specific imdb id
def get_json(data_path, id):
    if (id in os.listdir(data_path)):
        with open(data_path + "/" + id, 'r') as f:
            return json.loads(f.readline()) 
    else:
        return json.loads("{}")

# Float(able) checking for any type input
def is_float(element: any) -> bool:
    #If you expect None to be passed:
    if element is None: 
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False

# For each id in ids compares and filters based on attribute and specs
#   ids - initial list of movie ids
#   data_path - path storing json omdb data
#   attribute - type of filtering to apply, YEAR, IMDB, IMDBVOTE, META, RATED, GENRE, LANG, TITLE
#   comp - < = >
#   value - value to compare to
#   whitespaced_value - list of word(s) following the attribute for the title for multi-word filtering
# Returns filtered ids as a list of imdb ids
def get_movies_filtered(ids: list, data_path: str, attribute: str, comp: str, value: str, whitespaced_value) -> list:
    f_ids = []
    for id in ids:
        idjson = get_json(data_path, id)
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
        elif (attribute == "TITLE"):                                                          # TITLE - filter by title
            if (' '.join(whitespaced_value).upper() in idjson["Title"].upper()):
                f_ids.append(id)
    return f_ids

# Returns a dictionary of imdb id to movie path pairs
def get_movies_path(source_path, ids) -> dict:
    movie_dict = {}
    dirs = os.listdir(source_path)
    for dir in dirs:
        path = source_path+"/"+dir
        if (os.path.isdir(path)):
            files = os.listdir(path)
            for file in files:
                if("imdb-" in file):
                    result = re.search(r".imdb-(tt\d*).", file)
                    if (result.group(1) in ids):
                        movie_dict[result.group(1)] = path
                        break
    return movie_dict

# Calculates size of a specified folder, in bytes
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

# Converts bytes to gigabytes
# Currently rounds it whole, may want to add a decimal or two?
def byte_to_gig(num: int) -> int:
    return int(num / 1000000000)

# Create main list of all movie_ids
movie_ids = os.listdir(data_path)
filtered_ids = []

# Main command loop
proceed = False
while(not proceed):
    print("")
    total_ids = str(len(movie_ids))
    total_filtered = str(len(filtered_ids))
    q = input(total_filtered + "/" + total_ids + ">")
    qsep = q.split(" ")
    # Sometimes throws an error expecting this list to be a certain size
    try:
        qsep[3]
    except IndexError:
        qsep.append("")
    whitespaced_value = [x for x in qsep[2:] if x]

    # Process commands

    # HELP - Display command options
    if (qsep[0] == "help"):                                                                 
        print("options:")
        print("help     | show help")
        print("list     | lists selected movies or specify 'list all'")
        print("refresh  | updates the pulled movies")
        print("add      | YEAR, IMDB, META, IMDBVOTE (<=>) (Value)")
        print("add      | RATED, GENRE, LANG, TITLE (Value)")
        print("remove   | YEAR, IMDB, META, IMDBVOTE (<=>) (Value)")
        print("remove   | RATED, GENRE, LANG, TITLE (Value)")
        print("size     | get size of selected movies")
        print("copy     | (destination) copy movies to destination")
        print("rsync    | (destination) uses rsync to copy faster, linux only")
        print("path     | print out selected movies path(s)")
        print("import   | (path) import list of id's to select from file")
        print("export   | (path) export currently selected id's to file")
        print("quit     | exit program")

    # LIST - List selected or all movies, defaults to selected
    elif (qsep[0] == "list"):
        if (qsep[1] == "all"):
            for id in movie_ids:
                print(get_json(data_path, id)["Title"] + " (" + get_json(data_path, id)["Year"] + ")")
        else:
            for id in filtered_ids:
                print(get_json(data_path, id)["Title"] + " (" + get_json(data_path, id)["Year"] + ")")

    # Pull api for new movies
    elif (qsep[0] == "refresh"):
        collect_omdb(src, data_path)

    # ADD - Filter and add movies based on criteria from all movies
    elif (qsep[0] == "add"):
        new_additions = get_movies_filtered(movie_ids, data_path, qsep[1], qsep[2], qsep[3], whitespaced_value)

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
                        print(get_json(data_path, id)["Title"] + " (" + get_json(data_path, id)["Year"] + ")")
    
    # REMOVE - Filter and remove movies based on criteria from selected movies
    elif (qsep[0] == "remove"):
        to_remove = get_movies_filtered(filtered_ids, data_path, qsep[1], qsep[2], qsep[3], whitespaced_value)              

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
                        print(get_json(data_path, id)["Title"] + " (" + get_json(data_path, id)["Year"] + ")")

    # SIZE - Display size in GB of selected movies
    elif (qsep[0] == "size"):
        total_size = 0
        for id, path in get_movies_path(src, filtered_ids).items():
            total_size += get_folder_size(path)
        print(str(byte_to_gig(total_size)) + "GB")

    # Copy from movie src to specified destination using shutil.copytree
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
        fail_copied = 0
        for id, path in get_movies_path(src, filtered_ids).items():
            print("Copied " + str(total_copied) + " / " + str(len(filtered_ids)) + "   " + str(fail_copied) + " failed")
            print("Copying " + path)
            dest_path = dest + "/" + path.split("/")[-1]
            shutil.copytree(path, dest_path)
            total_copied += 1

    # Copy from movie src to specified destination using rsync
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
        fail_copied = 0
        for id, path in get_movies_path(src, filtered_ids).items():
            print("Copied " + str(total_copied) + " / " + str(len(filtered_ids)) + "   " + str(fail_copied) + " failed")
            print("Copying " + path)
            try:
                subprocess.call(["rsync", "-r", "--no-i-r", "--info=progress2", "--info=name0", path, dest])
                total_copied += 1
            except:
                print("Failed to copy")
                fail_copied += 1

    # Displays dictionary of movie id to path pairs of selected movies
    elif (qsep[0] == "path"):
        print(get_movies_path(src, filtered_ids))

    # Import list of movies from a file
    elif (qsep[0] == "import"):
        try:
            print("Importing " + ' '.join(qsep[1:]))
            with open(' '.join(qsep[1:]).strip(), 'r') as f:
                imported_ids = f.readlines()
                imported_ids = [i.strip() for i in imported_ids]
                print("Found " + str(len(imported_ids)) + " movie(s)")
                imported_count = 0
                not_imported_count = 0
                already_filtered = 0
                for import_id in imported_ids:
                    if import_id in movie_ids:
                        if import_id not in filtered_ids:
                            filtered_ids.append(import_id)
                            imported_count += 1
                        else:
                            already_filtered += 1
                    else:
                        not_imported_count += 1
                print("Imported " + str(imported_count))
                print("Don't have " + str(not_imported_count))
                print("Already had " + str(already_filtered))
                    
        except Exception as e:
            print("Failed to import")
            print(e)

    #Export list of movies to a file
    elif (qsep[0] == "export"):
        try:
            print("Exporting to " + ' '.join(qsep[1:]))
            with open(' '.join(qsep[1:]).strip(), 'w') as f:
                f.writelines('\n'.join(filtered_ids))
            print("Exported " + str(len(filtered_ids)) + " movie(s)")

        except Exception as e:
            print("Failed to export")
            print(e)

    # Ends the program
    elif (qsep[0] == "quit"):
        proceed = True

    # Default case, why doesn't python have switch
    else:
        print("Unknown, use 'help'")