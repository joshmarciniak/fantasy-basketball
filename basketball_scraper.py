import requests
from bs4 import BeautifulSoup
import pandas as pd

#list of months in the NBA season
month_list = ['october 2019', 'october 2020', 'september','october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june']
#creates dictionary of the months and values for each month
month_dictionary = {'Jan': '01', 'Feb': '02',  'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Sep': '09','Oct': '10', 'Nov': '11', 'Dec': '12'}
#creates dictionary of each NBA team and abbreviation value
team_dictionary = {
    'Atlanta Hawks': 'Atl', 'Boston Celtics': 'Bos', 'Brooklyn Nets': 'Bkn', 'Charlotte Hornets': 'Cha', 'Chicago Bulls': 'Chi', 'Cleveland Cavaliers': 'Cle', 'Dallas Mavericks': 'Dal',
    'Denver Nuggets': 'Den', 'Detroit Pistons': 'Det','Golden State Warriors': 'GSW', 'Houston Rockets': 'Hou', 'Indiana Pacers': 'Ind',
    'Los Angeles Lakers': 'LAL', 'Los Angeles Clippers': 'LAC', 'Memphis Grizzlies': 'Mem', 'Miami Heat': 'Mia', 'Milwaukee Bucks': 'Mil',
    'Minnesota Timberwolves': 'Min', 'New Orleans Pelicans': 'Nor', 'New York Knicks': 'NYK', 'Oklahoma City Thunder': 'OKC', 'Orlando Magic': 'Orl', 'Philadelphia 76ers': 'Phi',
    'Phoenix Suns': 'Pho', 'Portland Trail Blazers': 'Por', 'Sacramento Kings': 'Sac', 'San Antonio Spurs': 'SAS', 'Toronto Raptors': 'Tor', 'Utah Jazz': 'Uta', 'Washington Wizards': 'Was'
}

#basketball stat columns used by basketball-reference.com
df_columns = ['Date', 'GameID', 'Name', 'Team', 'OPP', 'Home', 'Away', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA',
                      '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK',
                      'TOV', 'PF', 'PTS', '+-' ]

#These are the links on basketball-reference.com for the past 5 NBA season games
season14_15 = 'https://www.basketball-reference.com/leagues/NBA_2015_games.html' #2014-15
season16_17 = 'https://www.basketball-reference.com/leagues/NBA_2017_games.html' #2016-2017
season17_18 = 'https://www.basketball-reference.com/leagues/NBA_2018_games.html' #2017-2018
season18_19 = 'https://www.basketball-reference.com/leagues/NBA_2019_games.html' #2018-2019
season19_20 = 'https://www.basketball-reference.com/leagues/NBA_2020_games.html' #2019-2020
    
def basketball_season_stat_scraper(season_URL):
    #This is the URL that is given (for this project basketball-reference.com was used).
    season = season_URL

    base_url = "https://www.basketball-reference.com/"
    month_link_array = []
    response = requests.get(season)
    soup = BeautifulSoup(response.text, 'lxml')
    #Gives season number (2019-2020)
    season = soup.find('h1').text.strip().split()[0]

    #finds the HTML element with the class "filter"
    body = soup.findAll(class_='filter')
    #collects the links for each month in the navigation menu
    months = body[0].findAll('a', href = True)
    #if the links collected above match months in the month_list, a value is created in array
    #that contains the month and the link from the navigation menu
    for month_link in months:
        if month_link.text.lower() in month_list:
            month_link = (month_link.text, f'{base_url}{month_link["href"]}')
            month_link_array.append(month_link)

    #creates dictionary containing month, URL, and an index
    page_dict = {'Month': [], 'Url': [], 'Index': []}
    box_link_array = []
    all_dates = []

    #accesses the months and pages in the month_link_array
    #they are stored as array[(month, link)]
    for month, page in month_link_array:
        page_link_array = []
        page_date_array = []
        #accesses the link provided by the current index in month_link_array
        response = requests.get(page)
        soup = BeautifulSoup(response.text, 'lxml')
        #finds all HTML elements with value 'tbody'
        table = soup.findAll('tbody')
        #finds all box score links on the provided page
        box_scores = table[0].findAll('a', href = True)

        #box_scores is a list of every <a> tagfrom table[0] (the first table on the page)
        for i in box_scores:
            #accesses text from the <a> tag to determine if the text is "Box Score"
            if i.text.strip() == 'Box Score':
                #collects the links that contain text "Box Score"
                #stores link in page_link_array to be accessed later
                page_link_array.append(f'{base_url}{i["href"]}')
            #accesses text from <a> tag to determine if it contains a comma
            if ',' in i.text.strip():
                #takes month day and year and stores it in numerical form in page_date_array
                date = i.text.strip().split(', ')
                year = date[2]
                date = date[1].split(' ')
                day = f'0{date[1]}' if len(date[1]) == 1 else date[1]
                mon = month_dictionary[date[0]]
                date = f'{year}{mon}{day}'
                #data will store like yearmonthday i.e (20201009) in an array
                page_date_array.append(date)

        #there are 4 links on each date page table entry and box score is the fourth link
        #appends url, month, and index into page_dict dictionary created earlier
        if len(page_link_array) == 0 or len(box_scores) / len(page_link_array) != 4:
            page_dict['Url'].append(page)
            page_dict['Month'].append(month)
            page_dict['Index'].append(len(page_link_array)
        else:
            page_dict['Url'].append(page)
            page_dict['Month'].append(month)
            page_dict['Index'].append(None)

        #appends page_link_array and page_date_array into box_link_array and all_dates
        box_link_array.append(page_link_array)
        all_dates.append(page_date_array)

    #uses pandas library to create data frames error_df and stat_df
    error_df = pd.DataFrame(columns = ['URL', 'Error'])
    stat_df = pd.DataFrame(columns = df_columns)

    #zip is used to pair iterators in tuples
    #pairs box_link_array values with all_dates values
    #this links the dates with the box score entrys on the pages
    for idx_pos, (l, d) in enumerate(zip(box_link_array, all_dates)):
        for link, date in zip(l, d):
            #creates output of the link and date that is being scraped
            print(f'{link}\n{date}')
            print(f'{idx_pos}- Currently Scraping {link}')
            try:
                #acquires the current link that is used for scraping
                response = requests.get(link)
                soup = BeautifulSoup(response.text, 'lxml')
                #finds table on link with the class "sortable stats_table"
                tables = soup.find('table', {'class': "sortable stats_table"})
                #not noneType object
                if tables is not None:
                    #this assembles game ID
                    #acquires team1 and team2 text from team_dictionary
                    team1 = tables.text.split('\n')[0]
                    parenthesis = team1.find('(')
                    team1 = team_dictionary[team1[:parenthesis - 1]]
                    table1 = tables.find('tbody')
                    table1 = table1.find_all('tr')
                    tables = soup.findAll('table', {'class': "sortable stats_table"})
                    team2 = tables[9].text.split('\n')[0]
                    if team2.strip() == 'Table':
                        team2 = tables[10].text.split('\n')[0]
                    parenthesis = team2.find('(')
                    team2 = team_dictionary[team2[:parenthesis-1]]
                    table2 = tables[9].find('tbody')
                    table2 = table2.find_all('tr')
                    #creates game_id from the team variables and the date from the current index
                    game_id = f'{date}-{team1}-{team2}'
                    print(f'({date})\tH: {team1}\tA: {team2}')
                    
                    #determines the value assigned to home and away team
                    for idx, t in enumerate([table1, table2]):
                        if idx == 0:
                            opp = team2
                            team = team1
                            home = 1
                            away = 0
                        else:
                            opp = team1
                            team = team2
                            home = 0
                            away = 1
                        #creates rows array
                        rows = []

                        #t is the table that is being accessed
                        for row in t:
                            #finds each table header which in this case is each player entry (name)
                            #each td under the th is the individual stats for that player based on the df_columns
                            name = row.findAll('th')[0].text
                            cols = row.findAll('td')
                            cols = [i.text.strip() for i in cols]
                            cols.append(name)
                            rows.append(cols)
                        
                        #each player in the rows array
                        for player in rows:
                            #each player entry has 21 different fields
                            #if any entry does no have 21 fields, it must be treated differently as incomplete
                            if len(player) < 21:
                                #some players have "Did Not Play" listed in their stats for this game
                                #need to take that players stats and set them all to 0
                                #adds zeroes to the player_dic
                                if 'Did Not' in player[0]:
                                    print(player, len(player))
                                    player_dic = {'Date': date, 'GameID': game_id, 'Name': player[-1], 'Team': team, 'OPP': opp,
                                                      'Home': home, 'Away': away, 'MP': 0, 'FG': 0, 'FGA': 0, 'FG%': 0, '3P': 0, '3PA': 0,
                                                      '3P%': 0, 'FT': 0, 'FTA': 0, 'FT%': 0,'ORB': 0, 'DRB': 0, 'TRB': 0, 'AST': 0,
                                                      'STL': 0, 'BLK': 0, 'TOV': 0, 'PF': 0, 'PTS': 0, '+-': 0
                                                      }
                                    stat_df = stat_df.append(player_dic, ignore_index = True)
                                    continue
                                #if "Did Not Play" not in the player[0] and entry not 21 fields, IGNORE player
                                else:
                                    print('IGNORE', player)
                                    continue
                            else:
                                #index is 0 if this is first player else it would be index for the index in player
                                player = [0 if i == ' ' else i for i in player]
                                #finds colon in MP field (minutes played)
                                colon = player[0].find(':')
                                #constructs time played field
                                time = f'{player[0][:colon]}.{player[0][colon + 1::]}'
                                #prints player name and number of fields (should be 21)
                                print(player, len(player))
                                #adds to player dictionary
                                #player[1] accesses entry containing Field Goals, player[2] Field Goal Attempts, etc.
                                player_dic = {'Date': date, 'GameID': game_id, 'Name': player[-1], 'Team': team, 'OPP': opp,
                                                  'Home':home, 'Away': away, 'MP': time, 'FG': player[1], 'FGA': player[2],
                                                  'FG%': player[3], '3P': player[4], '3PA': player[5],
                                                  '3P%': player[6],  'FT': player[7], 'FTA': player[8], 'FT%': player[9],
                                                  'ORB': player[10], 'DRB': player[11], 'TRB': player[12], 'AST': player[13],
                                                  'STL': player[14], 'BLK': player[15], 'TOV': player[16], 'PF': player[17],
                                                  'PTS': player[18], '+-': player[19]
                                                  }
                                #appends player game dictionary to the stat_df created using pandas library
                                stat_df = stat_df.append(player_dic, ignore_index = True)
                                continue
                print(f'Finished Scraping: {link}')
            #error/exception handling
            except Exception as e:
                raise
                print(f'Error Scraping: {link}')
                error = {'URL': {link}, 'Error': str(e)}
                error_df = error_df.append(error, ignore_index = True)
                error_df.to_csv(f'Errors_Season({season}).csv', line_terminator='\n', index = False)
                error_sender(error = str(e))

        #creates CSV file from the data frame
        stat_df.to_csv(f'Season({season}).csv', line_terminator='\n', index = False)
        message = f'Saved game stats for the {season} season to a csv'
        print(message)
    stat_df.to_csv(f'Season({season}).csv', line_terminator='\n', index = False)
    message = f'Saved game stats for the {season} season to a csv'
    print(message)
    
basketball_season_stat_scraper(season14_15)

    



