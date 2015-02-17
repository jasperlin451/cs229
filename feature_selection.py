import random
import numpy as np
from collections import defaultdict
from sklearn import cross_validation
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
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

def processTrainingData(numGames,X,y, toSkip):
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
        if j not in toSkip:
            X_row.append(team1Stats[j] - team2Stats[j])
      if game[0]:
        y.append(1)
      else:
        y.append(0)
      X.append(X_row)

old = 0
new  = 0.1
toSkip = []
while len(toSkip) < 10:
    numGames = len(final_games)
    numStats = 15
    maxScore = 0
    maxIndex = 0
    skip = 0
    skf = cross_validation.StratifiedKFold(y, n_folds=k, shuffle=True)
    while skip < numStats + ADDITIONAL_FEATURES:
        while skip in toSkip:
            skip += 1
        if skip == numStats + ADDITIONAL_FEATURES:
            break
        print skip
        gamesPlayedThreshold = 10
        X = []
        y = []
        toSkip.append(skip)
        processTrainingData(numGames, X, y, toSkip)

        logreg = LogisticRegression()
        scores = cross_validation.cross_val_score(logreg, X, y, cv=skf)
        print sum(scores)/10
        if sum(scores) > maxScore:
            maxScore = sum(scores)
            maxIndex = skip
        toSkip.remove(skip)
        skip += 1
    print maxIndex, maxScore
    toSkip.append(maxIndex)
    old = new
    new = maxScore
