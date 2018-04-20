from bs4 import BeautifulSoup
import requests
import json
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go
from date import date_conversion
import datetime

DBNAME = "movies.db"
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
t_lst = []
theater_and_state = {}

def get_theaters(response):
    address = response.split()
    city = address[1]
    state = address[2]
    zip_code = address[3]

    place_url = "https://www.moviefone.com/showtimes/{}-{}/{}/theaters/".format(city, state, zip_code)
    page_text = make_request_using_cache(place_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    theater_lst = page_soup.find_all('div', class_='theater')

    for t in theater_lst:
        theater_name = t.find('a').text
        link = t.find('a')['href']
        theater_and_link[theater_name] = link
        t_lst.append(theater_name)

    address_step = page_soup.find("div", class_ = 'address-keys')
    step = address_step.find('p', class_ = 'address')
    address = address_step.find('a').text
    state_split = address.split()[-2]
    for t in t_lst:
        if t not in theater_and_state:
            theater_and_state[t] = state_split
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
    return movie_lst

def convert_to_minutes(runtime):
    runtime_split = runtime.split()
    hour = int(runtime_split[0])
    min = int(runtime_split[2])

    final_time = hour*60 + min
    return final_time

database_info = []
def get_movie_info(movie):
    my_movie = []

    try:
        link_to_info = movie_and_link[movie]
        page_text = make_request_using_cache(link_to_info)
        page_soup = BeautifulSoup(page_text, 'html.parser')
        theater_info = page_soup.find('div', class_ = 'information')
        thater_info_further = theater_info.find('div', class_ = 'text')
        rating = theater_info.find('div', class_ = "movie-rating-score")
        my_movie.append(movie)

        if rating is not None:
            rating_both = rating.find_all('div', class_ = 'ratings-comments-sharing')
            meta = rating_both[0].text
            user = rating_both[1].text
            my_movie.append(meta)
            my_movie.append(user)
        else:
            meta = None
            user = None
            my_movie.append(meta)
            my_movie.append(user)

        date_and_rate = theater_info.find_all('p')
        for r in date_and_rate:
            try:
                if "Release Date" in r.text:
                    split = r.text.split(':')
                    date = split[1].strip()
                    real_date = date_conversion(date)
                    my_movie.append(real_date)
                if "PG-13" in r.text or "G" in r.text or "PG" in r.text or "R" in r.text or "NC-17" in r.text:
                    if 'hr' in r.text:
                        if 'min' in r.text:
                            if "|" in r.text:
                                split = r.text.split("|")
                                mpaa_rating = split[0]
                                runtime = convert_to_minutes(split[1])
                                my_movie.append(mpaa_rating)
                                my_movie.append(runtime)
            except:
                pass
    except:
        my_movie.append(movie)
        meta = None
        my_movie.append(meta)
        user = None
        my_movie.append(user)
        date = None
        my_movie.append(date)
        mpaa_rating = None
        my_movie.append(mpaa_rating)
        runtime = None
        my_movie.append(runtime)

    database_info.append(my_movie)
    return my_movie

def init_db():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("error occured")

    statement = '''
    DROP TABLE IF EXISTS 'Theaters';
    '''

    cur.execute(statement)
    statement = '''
    DROP TABLE IF EXISTS 'Movies'
    '''
    cur.execute(statement)

    statement = '''
    DROP TABLE IF EXISTS 'State'
    '''
    cur.execute(statement)

    statement = '''
    CREATE TABLE IF NOT EXISTS 'Theaters'(
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'Name' TEXT NOT NULL,
    'State' TEXT,
    'StateId' TEXT
    );
    '''
    cur.execute(statement)

    statement = '''
    CREATE TABLE IF NOT EXISTS 'State'(
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'State' TEXT NOT NULL
    );
    '''
    cur.execute(statement)


    statement = '''
    CREATE TABLE IF NOT EXISTS 'Movies' (
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'Name' TEXT,
    'Release Date' TEXT,
    'MPAARating' TEXT,
    'Runtime' INTEGER,
    'Metacritic Rating' INTEGER,
    'User Rating' INTEGER
    );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()
#     'Genres' TEXT


def insert_theater(lst):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    state_dict = foreign_keys()

    for inst in lst:
        insertion = (None, inst, None, state_dict[theater_and_state[inst]])
        statement = "INSERT INTO 'Theaters' "
        statement += 'VALUES (?, ?, ?, ?)'
        cur.execute(statement, insertion)

    conn.commit()
    conn.close()

def update_theater(lst):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    for x in theater_and_state:
        insertion = (theater_and_state[x], x)
        statement = 'UPDATE Theaters '
        statement += 'SET State = ? '
        statement += 'WHERE Name = ? '
        cur.execute(statement, insertion)

    conn.commit()
    conn.close()

def insert_state():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    state_ab = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

    for s in state_ab:
        insertion = (None, s)
        statement = "INSERT INTO 'State' "
        statement += 'VALUES (?, ?)'
        cur.execute(statement, insertion)

    conn.commit()
    conn.close()

lst_of_movies = []
dct_of_info_results = {}

def insert_movie_info(theaters):
    movie_and_count = {}

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    for t in theaters:
        results = get_movies_for_theater(t)
        for inst in results:
            # print(inst)
                if inst not in lst_of_movies:
                    lst_of_movies.append(inst)
    for l in lst_of_movies:
        info_results = get_movie_info(l)
        if l not in dct_of_info_results:
            dct_of_info_results[l] = info_results
    for x in dct_of_info_results:
        v = dct_of_info_results[x]
        try:
            insertion = (None, v[0], v[3], v[4], v[5], v[1], v[2])
            statement = "INSERT INTO 'Movies' "
            statement += 'VALUES (?, ?, ?, ?, ?, ?, ?)'
            cur.execute(statement, insertion)
        except:
            pass
    conn.commit()
    conn.close()

def foreign_keys():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
    SELECT State.Id, State.State
    FROM State
    '''
    cur.execute(statement)

    location_dict = {}
    for row in cur:
        location_dict[row[1]] = row[0]
    return location_dict

    conn.commit()
    conn.close()

def ratings_comparison():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
    SELECT Name, "Metacritic Rating", "User Rating"
    FROM Movies
    WHERE "Metacritic Rating" NOT NULL
    ORDER BY "Metacritic Rating"
    '''
    cur.execute(statement)

    names = []
    metacritic = []
    user = []

    for row in cur:
        if type(row[1]) == int:
            names.append(row[0])
            metacritic.append(row[1])
            user.append(row[2])

    trace1 = go.Bar(
    x=names,
    y=metacritic,
    name = "Metacritic Rating",
    marker=dict(
        color='rgb(191, 32, 21)',
        line=dict(
            color='rgb(191, 32, 21)',
            width=1.5)),)

    trace2 = go.Bar(
        x=names,
        y=user,
        name = "User Rating",
        marker=dict(
            color='rgb(255, 173, 51)',
            line=dict(
                color='rgb(255, 173, 51)',
                width=1.5),),)

    data = [trace1, trace2]
    layout = go.Layout(title='Metacritic Rating vs. User Rating',
            xaxis=dict(tickangle=-45), barmode='group')

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='grouped-bar-direct-labels')

    conn.commit()
    conn.close()

def mpaa_comparison():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    # statement = '''
    # SELECT MPAARating, [COUNT](MPAARating)
    # FROM Movies
    # WHERE MPAARating NOT NULL AND "Metacritic Rating" NOT NULL
    # GROUP BY MPAARating
    # '''
    # cur.execute(statement)
    statement = '''
    SELECT MPAARating, [COUNT](MPAARating)
    FROM Movies
    WHERE MPAARating = "PG-13" OR MPAARating ="PG" OR MPAARating = "R" OR MPAARating = "G" OR MPAARating = "Not Yet Rated"
    GROUP BY MPAARating
    '''
    cur.execute(statement)

    ratings = []
    count = []
    colors = ['#5DA5DA', '#FAA43A', '#F17CB0', 'DECF3F', '#F15854']

    for row in cur:
        ratings.append(row[0])
        count.append(row[1])

    labels = ratings
    values = count

    trace = go.Pie(labels=labels, values=values,
                   hoverinfo='label+value', textinfo='label+percent',
                   textfont=dict(size=20),
                   marker=dict(colors=colors))

    layout = go.Layout(
        title='Count of Movies with Each MPAA Rating')

    data = [trace]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='basic_pie_chart')

    conn.commit()
    conn.close()
    return ratings

def runtime_comparison():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
    SELECT Name, Runtime
    FROM Movies
    WHERE Runtime NOT NULL
    ORDER BY Runtime
    '''
    cur.execute(statement)

    names = []
    runtime = []

    for row in cur:
        names.append(row[0])
        runtime.append(row[1])

    trace2 = go.Bar(
        x=names,
        y=runtime,
        marker=dict(
            color='rgb(52, 135, 55)'))

    data = [trace2]
    layout = go.Layout(
        title='Movies By Runtime',
        xaxis=dict(
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            ),
            tickangle=-45),

        yaxis=dict(
            title='Runtime(Minutes)',
            titlefont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )))
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='text-hover-bar')

    conn.commit()
    conn.close()
    return runtime

def to_unix_time():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
    SELECT Name, "Release Date"
    FROM Movies
    WHERE "Release Date" NOT NULL
    ORDER BY "Release Date"
    '''

    d = []
    n = []
    cur.execute(statement)
    for row in cur:
        if "2018" in row[1]:
            d.append(row[1])
            n.append(row[0])

    trace = go.Scatter(
                    x=d,
                    y=n,
                    name = "Name",
                    line = dict(color = '#EA718A'),
                    opacity = 0.8)

    data = [trace]
    layout = dict(
        title = "Movies Released in 2018",
        xaxis = dict(
            range = ['2018-01-01','2018-12-31']))

    fig = dict(data=data, layout=layout)
    py.plot(fig, filename = "Manually Set Range")

    conn.commit()
    conn.close()

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
                    # city = words_lst[1]
                    # state = words_lst[2]
                    # zip_code = words_lst[3]
                    results = get_theaters(response)
                    for r in results:
                        theaters.append(r)
                    print('\nTheaters Near {}: '.format(words_lst[3]))
                except:
                    print("Please Enter a Valid Command")
                    continue
                for t in results:
                    print(item, t)
                    item +=1

            if 'create' in response:
                try:
                    insert_theater(results)
                    update_theater(results)
                    insert_movie_info(results)
                except:
                    print("\nMust get theaters first\n")

            if "compare" in response:
                try:
                    t = theaters
                    if words_lst[1] == "mpaa":
                        try:
                            mpaa_comparison()
                        except:
                            print('\nMust first fill database\n')
                    elif words_lst[1] == "ratings":
                        try:
                            ratings_comparison()
                        except:
                            print('\nMust first fill database\n')
                    elif words_lst[1] == "runtime":
                        try:
                            runtime_comparison()
                        except:
                            print('\nMust first fill database\n')
                    elif words_lst[1] == "release":
                        try:
                            to_unix_time()
                        except:
                            print('\nMust first fill database\n')
                    else:
                        print("\nEnter proper keyword to compare\n")
                except:
                    print("\nEnter Valid Compare Command(mpaa, runtime, ratings, release) and Ensure Data is in Database:\n")

if __name__ == "__main__":
    init_db()
    insert_state()
    interactive_prompt()
