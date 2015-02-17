import random
import numpy as np
from collections import defaultdict
from sklearn.svm import SVC 

MOMENTUM_THRESHOLD = 14
ADDITIONAL_FEATURES = 2
def acquireStatsUpToGame(teamGames, gameDate):
  teamStats = [0]*(numStats+ADDITIONAL_FEATURES)
  seasonWins = 0
  gameCount = 0
  gamesMap = defaultdict(int)
  for teamGame in teamGames:
    if teamGame < gameDate:
      for s in range(0,numStats):
        teamStats[s] += teamGames[teamGame][s]
      if teamGames[teamGame][0] > teamGames[teamGame][1]:
        gamesMap[teamGame] = 1
        seasonWins += 1
      else:
        gamesMap[teamGame] = 0
      gameCount += 1
  gameDateSorted = sorted(gamesMap.items(), key = lambda x: x[0], reverse=True)
  numRecentGames = 0
  recentWL = 0
  for i in range(0, MOMENTUM_THRESHOLD):
    if i == len(gameDateSorted):
      break
    numRecentGames += 1
    recentWL += gameDateSorted[i][1]
  for s in range(0, numStats):
    if gameCount > 0:
      teamStats[s] = (1.0*teamStats[s]) / gameCount
  # Add stat for w/l record
  if gameCount > 0:
    teamStats[numStats] = (seasonWins*1.0) / gameCount
  if numRecentGames:
    teamStats[numStats+1] = recentWL * 1.0 / numRecentGames
  # Add stat for recent w/l record
  return teamStats, gameCount

def processTrainingData(numGames,X,y):
  for i in range(0,numGames):
    game = final_games[i]
    team1 = game[1]
    team1Games = team_stats[team1]
    team1Stats, team1Count = acquireStatsUpToGame(team1Games, game[2])
    team2 = game[3]
    team2Games = team_stats[team2]
    team2Stats, team2Count = acquireStatsUpToGame(team2Games, game[4])
    if team1Count > gamesPlayedThreshold and team2Count > gamesPlayedThreshold:
      X_row = []
      for j in range(0,numStats+ADDITIONAL_FEATURES):
        X_row.append(team1Stats[j] - team2Stats[j])
      if game[0]:
        y.append(1)
      else:
        y.append(0)
      X.append(X_row)

numGames = len(final_games)
numStats = 15
gamesPlayedThreshold = 10
X = []
y = []
processTrainingData(numGames, X, y)
print 'Training Data Processed'

cutoff = int(round(len(X)*.5))
print cutoff
svm = SVC(degree=2).fit(X[0:cutoff], y[0:cutoff])
print svm.score(X[0:cutoff],y[0:cutoff])
print svm.score(X[cutoff:len(X)],y[cutoff:len(y)])
