from django.shortcuts import render
import requests
import datetime
from .models import *
from datetime import datetime, date
from bs4 import BeautifulSoup
import json
from django.urls import reverse
from django.shortcuts import redirect
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import re




#Function for an about section
def about(request):
    
    return render(request, 'about.html')


#Function for the results page
def match_results(request):

    #Get the results from the API
    url = "https://api-basketball.p.rapidapi.com/games/"

    querystring = {"season": '2022-2023', "league": '12'}

    payload = ""
    headers = {
        'X-RapidAPI-Key': "1d9ccb767bmsh67dd5bf1fd0cbadp186c7djsn18ce0ffbff90",
        'X-RapidAPI-Host': "api-basketball.p.rapidapi.com",
        }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    response = response.json()
 

    date_str = '2023-02-17T03:00:00+00:00'

    for match in response['response']:
            #Formatting the date
            date_str = match['date']
            
            # Convert the date string to a datetime object
            date_obj = datetime.fromisoformat(date_str[:-6])

            # Format the date as a string
            formatted_date = date_obj.strftime('%d %b, %Y')

            # Set the date to the formatted date
            match['date'] = formatted_date
    
    #  Render the results page
    return render(request, 'results.html', {"response": response['response']})


#Function for individual matches
def individual_matches(request, match_id):

    #Get the games from the API with the match ID as the parameter
    url = "https://api-basketball.p.rapidapi.com/games/"
    querystring = {"id":match_id}

    payload = ""
    headers = {
        'X-RapidAPI-Key': "1d9ccb767bmsh67dd5bf1fd0cbadp186c7djsn18ce0ffbff90",
        'X-RapidAPI-Host': "api-basketball.p.rapidapi.com",
    }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    response = response.json()
    

    # Get the IDs of the home and away teams from the response
    home_team_id = response['response'][0]['teams']['home']['id']
    away_team_id = response['response'][0]['teams']['away']['id']

    # Get the head-to-head response
    h2h_querystring = {"h2h": str(home_team_id) + '-' + str(away_team_id)}
    h2h_response = requests.request("GET", url, data=payload, headers=headers, params=h2h_querystring)
    h2h_response = h2h_response.json()
    
    #Extract the last name of the home and away teams
    last_names = { 
        "extract_home_last_name" : response['response'][0]['teams']['home']['name'].split()[-1],
        "extract_away_last_name" : response['response'][0]['teams']['away']['name'].split()[-1],

        #Gettting the scores as strings
        "home_score_str" : str(response['response'][0]['scores']['home']['total']),
        "away_score_str" : str(response['response'][0]['scores']['away']['total'])
    }

    # Hard coded cases
    if last_names["extract_home_last_name"] == "Blazers":
        last_names["extract_home_last_name"] = "trail-blazers"

    if last_names["extract_away_last_name"] == "Blazers":
        last_names["extract_away_last_name"] = "trail-blazers"

    for game in h2h_response['response']:
        # Format the date as a python datetime object
        game_date = datetime.strptime(game['date'], '%Y-%m-%dT%H:%M:%S%z')

        # Format the date as a string
        game['date'] = game_date.strftime('%b %d, %Y')

    #  Render the individual match page with the response and the last names of the teams and the scores and the head to head response
    return render(request, 'individual_match.html', {
        "response": response['response'], 
        "extract_home_last_name": last_names["extract_home_last_name"], 
        "extract_away_last_name": last_names["extract_away_last_name"], 
        "home_score_str": last_names["home_score_str"], 
        "away_score_str": last_names["away_score_str"],
        "h2h_response": h2h_response['response'] 
    })


#Function for the fixtures 
def match_fixtures(request):

    #Get the fixtures from the API
    url = "https://www.balldontlie.io/api/v1/games/"

    if request.method == 'POST':
        
        # User enters a date
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
    else:
        # Otherwise show today's games
        today = date.today().strftime('%Y-%m-%d')
        start_date = today
        end_date = today

    
    # If the user doesn't enter a date, show an error message
    if not start_date or not end_date:
            return render(request, 'fixtures.html', {'error_message': 'Please enter a date before filtering.'})
     
    querystring = {"start_date": start_date, "end_date": end_date}
    payload = ""
    headers = {}
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    response = response.json()
    
    

    
    for game in response['data']:
        # Format the date as a python datetime object
        game_date = datetime.strptime(game['date'], '%Y-%m-%dT%H:%M:%S.%fZ')

        #  Set the date to the formatted date
        game['date'] = game_date.strftime('%b %d, %Y')

        # Get logos of teams
        home_team_name = game["home_team"]["full_name"]
        away_team_name = game["visitor_team"]["full_name"]
        
        # Calling the get_team_logo function to get the logos
        game["home_team_logo"] = get_team_logo(home_team_name)
        game["away_team_logo"] = get_team_logo(away_team_name)

    # Sort the games by date
    sorted_response = sorted(response['data'], key=lambda x: x['date'])
     
    # Render the fixtures page with the response and the start and end dates
    context = {
        'response': sorted_response,
        'start_date': start_date,
        'end_date': end_date
    }

    return render(request, 'fixtures.html', context)


#Function to get the team logos
def get_team_logo(team_name):

    # Get the team logos from the API
    url = "https://api-basketball.p.rapidapi.com/teams"

    # Remove any whitespace between words and replace it with a single space
    team_name = " ".join(team_name.split())

    # One hardcoded case
    if team_name == "LA Clippers":
        team_name = "Los Angeles Clippers"

    querystring = {"name" : team_name}

    payload = ""
    headers = {
        'X-RapidAPI-Key': "1d9ccb767bmsh67dd5bf1fd0cbadp186c7djsn18ce0ffbff90",
        'X-RapidAPI-Host': "api-basketball.p.rapidapi.com",
        }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    response = response.json()

    #Extract a team logo from the response
    if response["results"] > 0:
        logo = response["response"][0]["logo"]
    else:
        # Return a default logo if team logo is not found
        logo = "https://via.placeholder.com/150"

    #Retrun the logo to the fixtures function
    return logo

#Function to get the player ids
def get_player_id(name_input):
    url = "https://www.balldontlie.io/api/v1/players"

    # Strip any special characters from the name
    name_input = re.sub('[^A-Za-z0-9\s]+', '', name_input) 

    #Join name into a single string with a space between each word
    name_input = " ".join(name_input.split())

    querystring = {"search" : name_input}

    payload = ""
    headers = {}

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    response = response.json()
    
    # define my_id with a default value
    my_id = None 

    # check if there are any entries in the data dictionary and if so, get the id
    if response['data']: 
        my_id = response['data'][0]['id']
    
    #return the id to the compare_players function
    return my_id

#Function to compare players
def compare_players(request):
    #Get the season averages from the API
    url = "https://www.balldontlie.io/api/v1/season_averages"

    player_names = []
    player_ids = []

    if request.method == 'POST':

        # Get all player names from the form
        player_names = [request.POST.get(f'player_chart_name_{i}') for i in range(1, 30) if request.POST.get(f'player_chart_name_{i}')]
        
        # Check if at least one player name is provided
        if not player_names:
            return render(request, 'compare_players.html', {'error_message': 'Please enter at least one player name.'})
        
        # Get player ids for each player
        player_ids = [get_player_id(player_name) for player_name in player_names]

        # Check if a player wasn't found
        if None in player_ids:
            return render(request, 'compare_players.html', {'error_message': 'One or more players were not found. Please check the spelling and try again.'})

    # create a list of responses for each player
    responses = []
    for player_id in player_ids:
        querystring = {"player_ids[]" : player_id}

        payload = ""

        response = requests.request("GET", url, data=payload, params=querystring)
        response = response.json()

        responses.append(response)

    #Create a list of dictionaries containing stats for each player
    player_stats = []
    for i, player_id in enumerate(player_ids):
        player_stat = {}
        player_stat['name'] = player_names[i]
        response = responses[i]
        for stat in response['data']:
            if stat['player_id'] == player_id:
                player_stat['games_played'] = stat['games_played']
                player_stat['pts'] = stat['pts']
                player_stat['min'] = stat['min']
                player_stat['fgm'] = stat['fgm']
                player_stat['fga'] = stat['fga']
                player_stat['fg3m'] = stat['fg3m']
                player_stat['fg3a'] = stat['fg3a']
                player_stat['ftm'] = stat['ftm']
                player_stat['fta'] = stat['fta']
                player_stat['reb'] = stat['reb']
                player_stat['ast'] = stat['ast']
                player_stat['stl'] = stat['stl']
                player_stat['blk'] = stat['blk']
                player_stat['turnover'] = stat['turnover']
        player_stats.append(player_stat)

    return render(request, 'compare_players.html', {"player_stats": player_stats})





#Function for standings
def standings(request):

    #Get the standings from the API 
    standings_url = "https://api-basketball.p.rapidapi.com/standings"

    querystring = {"season": '2022-2023', "league": '12'}
    headers = {
        'X-RapidAPI-Key': "1d9ccb767bmsh67dd5bf1fd0cbadp186c7djsn18ce0ffbff90",
        'X-RapidAPI-Host': "api-basketball.p.rapidapi.com",
    }

    standings_response = requests.request("GET", standings_url, headers=headers, params=querystring).json()
    
    # Render the standings page
    context = {
        "standings": standings_response["response"],
        
    }

    return render(request, 'standings.html', context)



def team_plot_chart(request):
    url = "https://api-basketball.p.rapidapi.com/statistics"

    # User enters input
    if request.method == 'POST':

        # Get all team names from the form
        team_names = [request.POST.get(f'team_chart_name_{i}') for i in range(1, 30) if request.POST.get(f'team_chart_name_{i}')]

       # Check if at least one team name is provided
        if not team_names:
            return render(request, 'team_chart.html', {'error_message': 'Enter some teams to plot the graph!'})

        season_id = request.POST.get('season_id')

        # Check if season_id is provided and in the correct format
        season_id = request.POST.get('season_id')
        if not season_id or not re.match(r'^\d{4}-\d{4}$', season_id):
            return render(request, 'team_chart.html', {'error_message': 'Enter a valid season in the format YYYY-YYYY!'})

        # Check if season year is after 2008
        season_year = int(season_id[:4])
        if season_year <= 2008:
            return render(request, 'team_chart.html', {'error_message': 'Enter a season year after 2008!'})

        # Check if any team name is invalid
        invalid_teams = [team_name for team_name in team_names if not get_team_id(team_name)]
        if invalid_teams:
            return render(request, 'team_chart.html', {'error_message': f'The following team names are invalid: {", ".join(invalid_teams)}!'})

        
        # Get team ids for each team
        team_ids = [get_team_id(team_name) for team_name in team_names]
        
        # Get the number of games won for each team
        games_won = []
        for team_id in team_ids:
            querystring = {"season": season_id, "league": "12", "team": team_id}
            headers = {
                'X-RapidAPI-Key': "1d9ccb767bmsh67dd5bf1fd0cbadp186c7djsn18ce0ffbff90",
                'X-RapidAPI-Host': "api-basketball.p.rapidapi.com",
            }
            response = requests.request("GET", url, headers=headers, params=querystring)
            data = response.json()
            
            #Gets the number of games won by the team
            if 'response' in data and data['response']:
                games_won.append(data['response']['games']['wins']['all']['total'])
            else:
                games_won.append(0)


        # Create a line chart using matplotlib
        # clear the current figure
        plt.clf() 
        plt.figure(figsize=(10, 8))
       
        # Plot the chart
        for i, team_name in enumerate(team_names):
            if len(team_names) < 4:
                my_width = 1 / len(team_names)
            else:
                my_width = 2.5 / len(team_names)
            plt.bar([i+1], [games_won[i]], label=team_name, width=my_width, edgecolor='black')
        plt.title('Games Won by ' + ', '.join(team_names) + ' in ' + season_id)
        plt.xticks(range(1, len(team_names)+1), team_names)
        plt.ylabel('Number of Games Won')
        plt.xlabel('Team Name')
        plt.legend()


        # Save the chart to a buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        
        # Encode the chart image as a base64 string
        chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Pass the chart image to the template context
        context = {'chart_image': chart_image}
        
        # Render the template with the chart image
        return render(request, 'team_chart.html', context)
    
    # User has not yet entered input 
    else:
        plt.clf() # clear the current figure
        plt.figure(figsize=(10, 8))
        plt.title('Enter some teams to plot the graph!')
        plt.ylabel('Number of Games Won')
        plt.xlabel('Team Name')
        plt.legend()

        # Save the chart to a buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        
        # Encode the chart image as a base64 string
        chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Pass the chart image to the template context
        context = {'chart_image': chart_image}
        
        # Render the template with the chart image
        return render(request, 'team_chart.html', context)


#Function to get team id
def get_team_id(name_input):
    url = "https://api-basketball.p.rapidapi.com/teams"
    
    name_input = re.sub('[^A-Za-z0-9\s]+', '', name_input)
    name_input = " ".join(name_input.split()) 
    querystring = {"search" : name_input}

    payload = ""
    headers = {
        'X-RapidAPI-Key': '1d9ccb767bmsh67dd5bf1fd0cbadp186c7djsn18ce0ffbff90',
        'X-RapidAPI-Host': 'api-basketball.p.rapidapi.com'
    }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    response = response.json()
 
    # Define my_id with a default value
    my_id = None 
    
    # Check if there are any entries in the data dictionary
    if response['response']:  
        my_id = response['response'][0]['id']
    
    # Return the team id to show_favorite_team function
    return my_id

#Function to scrape news arcticles from ESPN
def scrape_news(request):
    team = request.GET.get('team')
    hide_names = request.GET.get('hide_names') == 'true'


    # Set the URL of the ESPN.com page that contains the team's news
    url = f'https://www.espn.com/nba/team/_/name/{team}'

    # Send a GET request to the URL and parse the response with BeautifulSoup
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the news articles on the page
    news_articles = soup.find_all('article', {'class': 'contentItem'})

    # Create a list to store the news articles
    articles_list = []

    # Loop through each news article and extract the relevant information
    for article in news_articles:
        team_heading = soup.find('title').text.split('-')[0].strip()

        latest_article = article.find('a', class_='contentItem__content')
        
        # Check if latest_article is not None
        if latest_article is not None:
            headline = latest_article.find('h2', class_='contentItem__title').text.strip()
            link = latest_article['href']
        
            img = soup.find('img', class_='contentItem__logo')
            src = img['src']

            # Create a dictionary for the current article
            article_dict = {
                'team_heading': team_heading,
                'headline': headline,
                'link': link,
                'hide_names': hide_names,
            }

            #Append the article dictionary to the article list
            articles_list.append(article_dict)

    # Render the template with the news articles
    return render(request, 'scrape_news.html', {'articles_list': articles_list})


#Function to set favorite team
def set_favorite_team(request):
    if request.method == "POST":

        # Get the selected team from the form data
        team_name = request.POST.get("team")

        # Set the favorite team cookie
        response = redirect("show_favorite_team")
        response.set_cookie("favorite_team", team_name)

        return response
    else:

        # List of NBA teams
        teams = ["Milwaukee Bucks", "Brooklyn Nets", "Philadelphia 76ers", "Toronto Raptors", "Miami Heat", "Orlando Magic", "Atlanta Hawks", "Charlotte Hornets", "Washington Wizards", 
            "Indiana Pacers", "Cleveland Cavaliers", "Detroit Pistons", "Chicago Bulls", "New York Knicks", "Denver Nuggets", "Utah Jazz", "Oklahoma City Thunder", "Portland Trail Blazers",
            "Minnesota Timberwolves", "Memphis Grizzlies", "New Orleans Pelicans", "San Antonio Spurs", "Houston Rockets", "Dallas Mavericks", "Phoenix Suns", "Los Angeles Clippers", 
            "Sacramento Kings"]

        
        return render(request, "set_favorite_team.html", {"teams": teams})


def show_favorite_team(request):

    # Get the user's favorite team from the "favorite_team" cookie
    favorite_team = request.COOKIES.get("favorite_team")

    if not favorite_team:

        # If the "favorite_team" cookie is not set, redirect to the "set_favorite_team" view
        return redirect("set_favorite_team")

    # Check if the user wants to see the game results or news for their favorite team
    if request.GET.get("news"):

       # Get the team nickname from the get_team_nickname function for the favorite team
        nickname = get_team_nickname(favorite_team)
        
        #Use the scrape_news function to scrape the news articles of your favourite team
        my_redirect = redirect(reverse('scrape_news') + f"?team={nickname}&hide_names=true")
        return my_redirect

    # API request to get the games for the favorite team
    url = "https://api-basketball.p.rapidapi.com/games"

    team_id = get_team_id(favorite_team)

    querystring = {"league":"12","season":"2022-2023","team":team_id}
    headers = {
        'X-RapidAPI-Key': "1d9ccb767bmsh67dd5bf1fd0cbadp186c7djsn18ce0ffbff90",
        'X-RapidAPI-Host': "api-basketball.p.rapidapi.com",
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    response = response.json()

    for match in response['response']:
        date_str = match['date']
        date_obj = datetime.fromisoformat(date_str[:-6])
        formatted_date = date_obj.strftime('%d %b, %Y')
        match['date'] = formatted_date

    
    return render(request, "favorite_team.html", {"response": response['response'], "favorite_team": favorite_team})

#Function to get team nickname
def get_team_nickname(full_name):
    
    # Dictionary of NBA teams and their nicknames
    teams = {
    'atl': 'Atlanta Hawks',
    'bkn': 'Brooklyn Nets',
    'bos': 'Boston Celtics',
    'cha': 'Charlotte Hornets',
    'chi': 'Chicago Bulls',
    'cle': 'Cleveland Cavaliers',
    'dal': 'Dallas Mavericks',
    'den': 'Denver Nuggets',
    'det': 'Detroit Pistons',
    'gsw': 'Golden State Warriors',
    'hou': 'Houston Rockets',
    'ind': 'Indiana Pacers',
    'lac': 'LA Clippers',
    'lal': 'Los Angeles Lakers',
    'mem': 'Memphis Grizzlies',
    'mia': 'Miami Heat',
    'mil': 'Milwaukee Bucks',
    'min': 'Minnesota Timberwolves',
    'nop': 'New Orleans Pelicans',
    'nyk': 'New York Knicks',
    'okc': 'Oklahoma City Thunder',
    'orl': 'Orlando Magic',
    'phi': 'Philadelphia 76ers',
    'phx': 'Phoenix Suns',
    'por': 'Portland Trail Blazers',
    'sac': 'Sacramento Kings',
    'sas': 'San Antonio Spurs',
    'tor': 'Toronto Raptors',
    'utah': 'Utah Jazz',
    'was': 'Washington Wizards',
    }
    
    # Checks if the full name of the team is in the dictionary
    if full_name in teams.values():

        # Returns the nickname of the team
        return [k for k, v in teams.items() if v == full_name][0]
    else:
        return None

