# 206-final-project

Data Sources Used: https://moviefone.com


My code is structured for users to enter a location, and I return the theaters near them. After the user enters as many locations as they want, they type 'create' to put the movies and their information into the database. They then are able to compare the movies based on mpaa rating, runtime, release date, and critic ratings.

User Guide:

run: python3 final_proj.py

to get theaters in area:
  input: 'theaters' + 'city' + 'state' + 'zip'
     ex: theaters livingston nj 07039
  returns: list of theaters
if city has more than one word: enter as "word1-word2"

Once you have desired number of theaters:
  input: 'create'
  this will create database

Once database is created and populated, you can compare data with plotly
  input: 'compare' + option
    options: mpaa (compares movies based on MPAA Rating)
             ratings (compares moives based on metacritic ratings vs user ratings)
             runtime (compares movies based on runtime)
             release (compares movies based on release date)
