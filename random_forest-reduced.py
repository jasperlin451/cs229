import random
import numpy as np
from collections import defaultdict
from sklearn import cross_validation
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC 

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

def processData(numGames,X,y,Xtest,ytest,testSeason,toUse):
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
        if j in toUse:
            X_row.append(team1Stats[j] - team2Stats[j])
      if team1[3:] > testSeason and team1[3:] < str(int(testSeason)+1):
        Xtest.append(X_row)
        if game[0]:
          ytest.append(1)
        else:
          ytest.append(0)
      else:
        if game[0]:
          y.append(1)
        else:
          y.append(0)
        X.append(X_row)

def normalizeData(X):
  for i in range(0,len(X[0])):
    xmax = np.max(X[:,i])
    xmin = np.min(X[:,i])
    for j in range(0,len(X)):
      X[j,i] = ((X[j,i] - xmin)*1.0)/(xmax - xmin)

toUse = [0,3,9,10,12,15,16,6]
numGames = len(final_games)
numStats = 15
gamesPlayedThreshold = 10
k = 10
X = []
y = []
Xtest = []
ytest = []
testSeason = '1997'
processData(numGames, X, y, Xtest, ytest, testSeason, toUse)
X = np.array(X)
Xtest = np.array(Xtest)
normalizeData(X)
normalizeData(Xtest)
print "Data Processed"
#skf = cross_validation.StratifiedKFold(y, n_folds=k, shuffle=True)
rf = RandomForestClassifier(n_estimators=500, max_depth=11)
totalTest = 0
totalTrain = 0
for i in range(0,10):
  rf.fit(X,y)
  totalTest += rf.score(Xtest,ytest)
  totalTrain += rf.score(X,y)
print "Test: ", totalTest/10
print "Train: ", totalTrain/10

"""for i in range(2,14):
  #i = 7 seems to yield best results
  rf = RandomForestClassifier(n_estimators=100, max_depth=i)
#cutoff = int(round(len(X)*.8))
#rf.fit(X[0:cutoff],y[0:cutoff])
#print rf.score(X[0:cutoff],y[0:cutoff])
#print rf.score(X[cutoff:len(X)],y[cutoff:len(y)])
  scores = cross_validation.cross_val_score(rf, X, y, cv=skf)
  print i
  print sum(scores)/10"""
