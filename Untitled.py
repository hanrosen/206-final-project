from bs4 import BeautifulSoup
import requests
import json

CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def make_request_using_cache(baseurl, params= {}, auth = None):
    unique_ident = params_unique_combination(baseurl,params)

    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        # Make the request and cache the new data
        print("Making a request for new data...")
        resp = requests.get(baseurl, params, auth=auth)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

baseurl =  "https://www.moviefone.com/"
theater_and_link = {}

def get_theaters(city = None, state = None, zip_code = None):
# use zip code from interactive prompt to make a request to fandango in order to get a list of theaters at that time
    place_url = "https://www.moviefone.com/showtimes/{}-{}/{}/theaters/".format(city, state, zip_code)
    page_text = make_request_using_cache(place_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    theater_lst = page_soup.find_all('div', class_='theater')
    # print(theater_lst)
    t_lst = []

    for t in theater_lst:
        theater_name = t.find('a').text
        link = t.find('a')['href']
        theater_and_link[theater_name] = link
        t_lst.append(theater_name)
    return t_lst

movie_and_link = {}
movie_lst = []

def get_movies_for_theater(theater):
    link_to_theater = theater_and_link[theater]
    page_text = make_request_using_cache(link_to_theater)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    movie_data = page_soup.find_all('div', class_ = 'movie-listing')

    for movie in movie_data:
        title = movie.find('div', class_ = "movietitle")
        final_title = title.find('a').text
        final_title_link = title.find('a')['href']
        movie_and_link[final_title] = final_title_link
        movie_lst.append(final_title)
        # print(final_title)
    return movie_lst
    # movie_lst=[]
def convert_to_minutes(runtime):
    runtime_split = runtime.split()
    hour = int(runtime_split[0])
    min = int(runtime_split[2])

    final_time = hour*60 + min
    return final_time

database_info = []
def get_movie_info(movie):
    my_movie = []
    link_to_info = movie_and_link[movie]
    page_text = make_request_using_cache(link_to_info)
    page_soup = BeautifulSoup(page_text, 'html.parser')

    theater_info = page_soup.find('div', class_ = 'information')
    thater_info_further = theater_info.find('div', class_ = 'text')
    rating = theater_info.find('div', class_ = "movie-rating-score")
    rating_both = rating.find_all('div', class_ = 'ratings-comments-sharing')
    # print(rating_both)

    my_movie.append(movie)
    meta = rating_both[0].text
    user = rating_both[1].text
    my_movie.append(meta)
    my_movie.append(user)
    # print(meta, user)
    # print(my_movie)
    date_and_rate = theater_info.find_all('p')
    for r in date_and_rate:
        if "Release Date" in r.text:
            split = r.text.split(':')
            date = split[1].strip()
            my_movie.append(date)
        if "PG-13" in r.text or "G" in r.text or "PG" in r.text or "R" in r.text or "NC-17" in r.text:
            if 'hr' in r.text:
                if 'min' in r.text:
                    split = r.text.split("|")
                    mpaa_rating = split[0]
                    runtime = convert_to_minutes(split[1])
                    my_movie.append(mpaa_rating)
                    my_movie.append(runtime)
        if "Genres" in r.text:
            genres = []
            for g in r.text.split()[1:]:
                genres.append(g)
            my_movie.append(genres)

    database_info.append(my_movie)
    return my_movie

def load_help_text():
    with open('final_help.txt') as f:
        return f.read()

def interactive_prompt():
        help_text = load_help_text()
        response = ''
        while response != 'exit':
            response = input('Enter a Command or help for instructions: ')
            words_lst = response.split()
            if response == 'help':
                print(help_text)
                continue
            elif response == "exit":
                print("Bye!")
            item = 1
            if "theaters" in response:
                if len(words_lst) > 4:
                    print('Please Enter a Valid Command')
                try:
                    theaters = []
                    city = words_lst[1]
                    state = words_lst[2]
                    zip_code = words_lst[3]
                    # print(words_lst)
                    results = get_theaters(city, state, zip_code)
                    for r in results:
                        theaters.append(r)
                    print('\nTheaters Near {}: '.format(words_lst[3]))
                except:
                    print("Please Enter a Valid Command")
                    continue
                for t in theaters:
                    print(item, t)
                    item +=1

            if "movies" in response:
                if len(theaters) == 0:
                    print("Get theater list first")
                movies = []
                try:
                    item = theaters[int(words_lst[1])-1]
                    results = get_movies_for_theater(item)
                    for r in results:
                        movies.append(r)
                    print("\nMovies Showing at {}: ".format(item.strip()))
                    item = 1
                    for m in results:
                        print(item, m)
                        item += 1
                except:
                    print('Must have theater list before requesting movies OR Must enter valid number of movie')
                    continue
            if "info" in response:
                info = []
                try:
                    i = movies[int(words_lst[1])-1]
                    # print(i)
                    new_results = get_movie_info(i)
                    # for r in new_results:
                    #     info.append(r)
                    print("\nInfo for {}: ".format(i.strip()))
                    item = 1
                    for m in new_results:
                        print(item, m)
                        item += 1
                except:
                    print("Invalid Command. Try Again")


if __name__ == "__main__":
    interactive_prompt()
