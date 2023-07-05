from .views import *
from django.test import TestCase, Client
from django.urls import reverse
from django.shortcuts import redirect, render
import requests
from datetime import datetime

# FINISHED
class StandingsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('standings')
        
    def test_standings_view_success(self):
        # Test to see if response is a success
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
    def test_standings_view_content(self):
        # Test to see if the response contains conferences
        response = self.client.get(self.url)
        self.assertContains(response, 'Standings')
        self.assertContains(response, 'Western Conference')
        self.assertContains(response, 'Eastern Conference')
        
    def test_standings_view_context(self):
        # Test the context returned to see if we have correct values
        response = self.client.get(self.url)
        self.assertIn('standings', response.context)
        self.assertIn('games', response.context)


# FINISHED
class GetPlayerIdTestCase(TestCase):
    def test_get_player_id(self):
        # Test case where the player is found
        player_id = get_player_id('Lebron James')
        self.assertEqual(player_id, 237)

    def test_player_not_found(self):
        # Test case where the player is not found
        player_id = get_player_id('John Doe')
        self.assertIsNone(player_id)

    def test_case_insensitivity(self):
        # Test case where the player name is not case sensitive
        player_id_uppercase = get_player_id('LeBron James')
        player_id_lowercase = get_player_id('lebron james')
        self.assertEqual(player_id_uppercase, player_id_lowercase)

    def test_special_characters(self):
        # Test case where the player name contains special characters
        player_id = get_player_id("Lebron James--")
        self.assertEqual(player_id, 237)

    def test_whitespace(self):
        # Test case where the player may contain whitespace
        player_id = get_player_id("  Lebron   James  ")
        self.assertEqual(player_id, 237)



# FINISHED
class GetTeamIdTestCase(TestCase):
    def test_get_player_id(self):
        # Test case where the team is found
        team_id = get_team_id('Los Angeles Lakers')
        self.assertEqual(team_id, 145)

    def test_team_not_found(self):
        # Test case where the team is not found
        team_id = get_team_id('Pos Pngeles Pakers')
        self.assertIsNone(team_id)

    def test_case_insensitivity(self):
        # Test case where the team is not case sensitive
        team_id_uppercase = get_team_id('Los Angeles Lakers')
        team_id_lowercase = get_team_id('los angeles lakers')
        self.assertEqual(team_id_uppercase, team_id_lowercase)

    def test_special_characters(self):
        # Test case where the team name contains special characters
        team_id = get_team_id("Los Angeles Lakers--")
        self.assertEqual(team_id, 145)

    def test_whitespace(self):
        # Test case where the team may contain whitespace
        team_id = get_team_id("   Los   Angeles  Lakers  ")
        self.assertEqual(team_id, 145)


# FINISHED
class GetTeamLogoTestCase(TestCase):
    def test_get_team_logo_found(self):
        # Test case where team logo is found
        logo = get_team_logo('Indiana Pacers')
        self.assertTrue(logo == 'https://media-3.api-sports.io/basketball/teams/143.png' or logo == 'https://media.api-sports.io/basketball/teams/143.png')


    def test_get_team_logo_not_found(self):
        # Test case where team logo is not found
        logo = get_team_logo('Fake Team')
        self.assertEqual(logo, 'https://via.placeholder.com/150')

    def test_get_team_logo_capitals(self):
        # Test case to see if capitalization matters
        logo = get_team_logo('inDiAnA pAcErs')
        self.assertTrue(logo == 'https://media-3.api-sports.io/basketball/teams/143.png' or logo == 'https://media.api-sports.io/basketball/teams/143.png')

    def test_get_team_logo_whitespace(self):
        # Test case to see if whitespace matters
        logo = get_team_logo(' inDiAnA  pAcErs ')
        self.assertTrue(logo == 'https://media-3.api-sports.io/basketball/teams/143.png' or logo == 'https://media.api-sports.io/basketball/teams/143.png')


# FINISHED
class MatchResultsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('results')
        
    def test_success(self):
        # Test to see if response is a success
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_list_is_not_empty(self):
        # Test to see if match list is not empty
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        matches = response.context['response']
        self.assertGreater(len(matches), 0)

    def test_correct_date_formatting(self):
        # Test to see if dates are formatted correctly
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        matches = response.context['response']
        for match in matches:
            self.assertTrue(isinstance(match['date'], str))
            self.assertTrue(bool(re.match('\d{2} [A-Z][a-z]{2}, \d{4}', match['date'])))



class MatchFixturesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('match_fixtures')
        
    def test_fixtures_view_success(self):
        # Test to see if response is a success
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_fixtures_view_post_request(self):
        # Test to see if a POST request returns a success
        data = {'start_date': '2023-02-23', 'end_date': '2023-02-24'}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_fixtures_view_response_contains_data(self):
        # Test to see if the response contains game data
        response = self.client.get(self.url)
        self.assertContains(response, 'data')

    def test_fixtures_view_response_sorted_by_date(self):
        # Test to see if the response is sorted by date
        response = self.client.get(self.url)
        games = response.context['response']
        for i in range(len(games)-1):
            date1 = datetime.strptime(games[i]['date'], '%b %d, %Y')
            date2 = datetime.strptime(games[i+1]['date'], '%b %d, %Y')
            self.assertLessEqual(date1, date2)
    



# FINISHED
class IndividualMatchTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('individual_match', kwargs={'match_id': 327010})
        
    def test_success(self):
        # Test to see if response is a success
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        # Test specific match to see if the context contains the expected data
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['extract_home_last_name'], 'Pacers')
        self.assertEqual(response.context['extract_away_last_name'], 'Bulls')
        self.assertEqual(response.context['home_score_str'], '117')
        self.assertEqual(response.context['away_score_str'], '113')

    def test_h2h_response(self):
        # Test to see if the h2h_response contains the expected data
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        h2h_response = response.context['h2h_response']
        self.assertTrue(isinstance(h2h_response, list))
        for game in h2h_response:
            self.assertTrue('date' in game)
            self.assertTrue('teams' in game)
            self.assertTrue('time' in game)
            self.assertTrue('name' in game['teams']['home'])
            self.assertTrue('name' in game['teams']['away'])



# FINISHED
class ComparePlayersTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('compare_players')
        
    def test_success(self):
        # Test to see if response is a success
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_one_player(self):
        # Test case where one player is specified in the form
        response = self.client.post(reverse('compare_players'), {'player_chart_name_1': 'LeBron James'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'LeBron James')

    def test_multiple_players(self):
        # Test case where multiple players are specified in the form
        response = self.client.post(reverse('compare_players'), {'player_chart_name_1': 'LeBron James', 'player_chart_name_2': 'Kevin Durant'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'LeBron James')
        self.assertContains(response, 'Kevin Durant')

    def test_sort_by_points(self):
        # Test case where the player stats are sorted by points
        response = self.client.get(reverse('compare_players'), {'sort': 'pts'})
        self.assertEqual(response.status_code, 200)
        # Verify that the player stats are sorted by points in descending order
        pts_list = [player['pts'] for player in response.context['player_stats']]
        self.assertEqual(pts_list, sorted(pts_list, reverse=True))

    def test_invalid_post_request(self):
        # Test case where no player names are specified in the form
        response = self.client.post(reverse('compare_players'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter at least one player name.')

    def test_invalid_player_name(self):
        # Test case where an invalid player name is specified in the form
        response = self.client.post(reverse('compare_players'), {'player_chart_name_1': 'Invalid Player Name'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'One or more players were not found. Please check the spelling and try again.')


# FINISHED
class TeamPlotChartTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('team_chart')
        
    def test_plot_view_success(self):
        # Test to see if response is a success
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_request_with_valid_data(self):
        # Test to see if the view returns a chart image when a valid POST request is made
        response = self.client.post(self.url, {
            'team_chart_name_1': 'Lakers',
            'team_chart_name_2': 'Celtics',
            'season_id': '2019-2020'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<img src="data:image/png;base64,', count=1)

    def test_post_request_with_invalid_data(self):
        # Test to see if the view returns an error message when an invalid POST request is made
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter some teams to plot the graph!')

    def test_post_request_with_invalid_season_format(self):
        # Test to see if the view returns an error message when an invalid season format is provided
        response = self.client.post(self.url, {
            'team_chart_name_1': 'Lakers',
            'team_chart_name_2': 'Celtics',
            'season_id': '2021'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid season in the format YYYY-YYYY!')

    def test_post_request_with_season_before_2008(self):
        # Test to see if the view returns an error message when a season before 2008 is provided
        response = self.client.post(self.url, {
            'team_chart_name_1': 'Lakers',
            'team_chart_name_2': 'Celtics',
            'season_id': '2007-2008'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a season year after 2008!')

    def test_post_request_with_invalid_team_name(self):
        # Test to see if the view returns an error message when an invalid team name is provided
        response = self.client.post(self.url, {
            'team_chart_name_1': 'Lakers',
            'team_chart_name_2': 'FakeTeam',
            'season_id': '2019-2020'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The following team names are invalid: FakeTeam!')

    def test_get_request(self):
        # Test to see if the view returns a chart image when a GET request is made
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<img src="data:image/png;base64,', count=1)



# FINISHED
class ScrapeNewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('scrape_news')
        
    def test_news_view_success(self):
        # Test to see if response is a success
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_articles_specific_team(self):
        url = reverse('scrape_news') + '?team=lal'
        response = self.client.get(url)

        # Verify that the response contains at least one article for the Lakers
        self.assertGreater(len(response.context['articles_list']), 0)
        self.assertEqual(response.context['articles_list'][0]['team_heading'], 'Los Angeles Lakers Basketball')
        self.assertIn('headline', response.context['articles_list'][0])
        self.assertIn('link', response.context['articles_list'][0])

    def test_articles_multiple_results(self):
        # Test to see if multiple articles are returned for a team
        url = reverse('scrape_news') + '?team=mia'
        response = self.client.get(url)

        # Verify that the response contains more than one article for Miami Heat
        self.assertGreater(len(response.context['articles_list']), 1)

        # Test to see if all articles belong to Miami Heat
        for article in response.context['articles_list']:
            self.assertEqual(article['team_heading'], 'Miami Heat Basketball')
            self.assertIn('headline', article)
            self.assertIn('link', article)

    def test_articles_no_results(self):
        # Test to see if no results are returned for invalid team name
        url = reverse('scrape_news') + '?team=invalidteamname'
        response = self.client.get(url)

        # Verify that the response contains no articles for invalid team name
        self.assertEqual(len(response.context['articles_list']), 0)




# FINISHED
class SetFavoriteTeamTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('set_favorite_team')
        
    def test_set_favorite_view_success(self):
        # Test to see if response is a success
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_set_favorite_cookie(self):
        # Test to see if setting the favorite team cookie works
        team = "Milwaukee Bucks"
        response = self.client.post(self.url, {'team': team})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.cookies['favorite_team'].value, team)
        self.assertRedirects(response, reverse('show_favorite_team'))



# FINISHED
class ShowFavoriteTeamTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('show_favorite_team')
        
    def show_favorote_view_success(self):
        # Test to see if response is a success
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_favorite_team_cookie_not_set(self):
        # Test to see if user is redirected to set_favorite_team view when cookie is not set
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('set_favorite_team'))

    def test_favorite_team_api_request_success(self):
        # Test to see if API request for favorite team's games returns a successful response
        team = "Milwaukee Bucks" # Replace with user's favorite team
        team_id = get_team_id(team)
        querystring = {"league": "12", "season": "2021-2022", "team": team_id}

        headers = {
            'X-RapidAPI-Key': "1d9ccb767bmsh67dd5bf1fd0cbadp186c7djsn18ce0ffbff90",
            'X-RapidAPI-Host': "api-basketball.p.rapidapi.com",
        }

        response = requests.get("https://api-basketball.p.rapidapi.com/games", headers=headers, params=querystring)
        self.assertEqual(response.status_code, 200)

    def test_favorite_team_response_contains_games(self):
        # Test to see if response from API request for favorite team's games contains games
        team = "Milwaukee Bucks" # Replace with user's favorite team
        team_id = get_team_id(team)
        querystring = {"league": "12", "season": "2021-2022", "team": team_id}

        headers = {
            'X-RapidAPI-Key': "1d9ccb767bmsh67dd5bf1fd0cbadp186c7djsn18ce0ffbff90",
            'X-RapidAPI-Host': "api-basketball.p.rapidapi.com",
        }

        response = requests.get("https://api-basketball.p.rapidapi.com/games", headers=headers, params=querystring)
        self.assertGreater(len(response.json()['response']), 0)