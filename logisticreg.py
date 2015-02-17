import random
import numpy as np
from collections import defaultdict
from sklearn import cross_validation
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression

MOMENTUM_THRESHOLD = 10
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

logreg = LogisticRegression()
k = 10
skf = cross_validation.StratifiedKFold(y, n_folds=k, shuffle=True)
scores = cross_validation.cross_val_score(logreg, X, y, cv=skf)
print scores
print sum(scores)/10
logreg.fit(X,y)
print logreg.score(X,y)

"""
numCorrect = 0
for i in range(0,len(X)):
    if X[i][0]-X[i][1] > 0:
      predict = 1
    else:
      predict = 0
    if predict == y[i]:
      numCorrect += 1
#print (1.0*numCorrect)/len(X)"""
