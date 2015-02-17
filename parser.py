import snap
import csv
import collections

def monthToNum(date):

    return{
            'Jan' : '3',
            'Feb' : '4',
            'Mar' : '5',
            'Apr' : '6',
            'May' : '7',
            'Oct' : '0',
            'Nov' : '1',
            'Dec' : '2'
    }[date]

csv_scores = open('NBA_Scores.csv', 'r')
player_scores = csv.reader(csv_scores, delimiter='#')

# Set up tables for training data and stats
# team_stats table has format (team+season) -> dict. This dict has format
# (month-day-opponentname) -> array(stats). For the array of stats, the
# important data is in indices 0-14. Ignore 15-18.

# data = list(score, oppscore, fgm, fga, ftm, fta, tpm, tpa, orb, drb, ast, stl,
# to, blk, foul)

team_stats = collections.defaultdict(dict)
team_overall = collections.defaultdict(dict)
for row in player_scores:
    season = row[15]
    if season >= '1998':
        continue
    team = row[16]
    opp = row[20]
    month = monthToNum(row[18])

    day = row[19]
    if len(day) == 1:
      day = '0' + day
    data = row[17:18] + row[21:22] + row[23:31] + row[32:38]

    # Extract current team from list of teams
    ts = team_stats[team+season]
    if (month+"-"+day+"-"+opp) not in ts:
        ts[month+"-"+day+"-"+opp] = [0]*19

    # Extract (and initialize) point total for current team's game and add
    # players statistics to the total
    gs = ts[month+"-"+day+"-"+opp]
    for i in range(0, 15):
        if (i == 0):
            if (not data[0].isdigit()):
                continue
            elif (int(data[0]) > gs[0]):
                gs[0] = int(data[0])
        elif (i == 1 and data[i].isdigit()):
            gs[1] = int(data[1])
        elif (i != 1):
            gs[i] += int(data[i])
    gs[15] = team+season
    gs[16] = month+"-"+day+"-"+opp
    gs[17] = opp+season
    gs[18] = month+"-"+day+"-"+team

# Extract training data from the team scores (filter out bad data as well)
# format of final_games is (team1 won (T/F), team1 key, game key, team2
# key, game key) for easy lookup in team_stats table
games = []
for tkey in team_stats:
    for gkey in team_stats[tkey]:
        game = team_stats[tkey][gkey]
        if game[0] < 50 or game[1] < 50:
            continue
        info = [game[0] > game[1]] + game[15:19]
        if info[3] in team_stats and info[4] in team_stats[info[3]]:
            games.append(info)

final_games = []
# filter out bad games (scores don't match)
for g in range(0,len(games)):
    if team_stats[games[g][3]][games[g][4]][0] == team_stats[games[g][1]][games[g][2]][1]:
        final_games.append(games[g])

