import random
import re
import functools
import heapq

# Dice Roller by Citronella
# 
# Example rolls:
# 3d6    - roll three 6-sided dice, add the results
# 4d8k2  - roll four 8-sided dice, take the highest 2 results and add them.
# 4d8l2  - roll four 8-sided dice, take the lowest 2 results and add them.
# 5d4!   - roll five 4-sided dice, roll again if you get a 4; All rolled values are summed.
# 5*2    - you can do math, I guess
# 7d20+3 - you can do math with dice too!
#
#
# Future releases:
# Catch exception for:
#	d0 - invalid roll (or maybe make it a coin toss)
#	5d3k10 - keep more rolls than rolled
# Implement comments in rolling:
#	-> 2d20 #attack
#		=> attack 1d20: (15 + 3) = 18
# Implement Fudge/Fate dice (1dF)
#	Roll results: +, 0 -. No explosion, no k/l.
#	Adds up for xdF, e.g. 4dF: (+, +, -, 0) = 1
# Implement explosion >n (1d10!>9)
# Implement success counter (5d6>=4)
# Maybe display dropped rolls for k and l

def flatten(l): 
	if type(l) is list:
		return flatten(l[0]) + (flatten(l[1:]) if len(l) > 1 else [])
	else: 
		return [l]

def parse(dadu): #parse input to list for easier processing
	return re.split('([+\-*/^])', re.sub(r"\s+", "", dadu))

def evaldice(elem): 
#evaluate all the dice expressions, leaving op alone
	if re.match("^[0-9+\-*/]*$", elem):
		return elem
	elif elem == "^":
		return "**"
	else:
		return roll(elem)
	#how do I catch exception here?


def roll(dice): #rolls 5d10k2!
	diceexp = [] #["5d10", "k2", "!"]
	actualdie = [] #[attempts, 5, 10, [result]]

	def makedie(raw): #5d10k2! => diceexp
		splitted = list(filter(None, re.split("(k|l)", raw))) #split, remove blanks. => ["5d10", "k", "2!"]
		thedie = [splitted[0]]
		mods = [splitted[i] + splitted[i+1] for i in range(1, len(splitted), 2)]
		thedie.extend(mods)
		diceexp = []
		for m in thedie:
			mod = list(filter(None, re.split(r"(!)", m))) #separate the "!"
			diceexp.extend(mod)
		return diceexp

	def parsedie(exp): #5d10 => actualdie, e.g. [1, 5, 10, [2,6,9,10,9]]
		dice = exp[0]
		nonlocal actualdie
		nonlocal diceexp
		attempt = 1 
		actualdie.append(attempt) 
		actualdie.extend(list(map(int, dice.split('d')))) 

		rolls = actualdie[1]
		limit = actualdie[2]
		res = []

		for _ in range(rolls):
			indivroll = random.randint(1, limit)
			res.append(indivroll)

		actualdie.append(res)
		actualdie[1] = sum(1 for i in res if i == limit)
		diceexp = exp[1:]

	def evalattrib(diceexp):
		nonlocal actualdie
		for attrib in diceexp:
			if attrib == "!": #explode dice
				actualdie = evalexpl(actualdie)
			elif attrib[0] == "k": #keep n highest rolls
				num = int(attrib[1:])
				actualdie[3] = heapq.nlargest(num, actualdie[3])
				actualdie[1] = sum(1 for i in actualdie[3] if i == actualdie[2]) #resolve explosions
			elif attrib[0] == "l": #keep lowest n rolls
				num = int(attrib[1:])
				actualdie[3] = heapq.nsmallest(num, actualdie[3])
				actualdie[1] = sum(1 for i in actualdie[3] if i == actualdie[2])
		return actualdie
		#might just make one function for k and l considering their similarity.

	def evalexpl(die):
		try:
			res = []
			attempt = die[0]
			rolls = die[1]
			limit = die[2]

			if rolls == 0: #nothing to explode
				die[3] = flatten(die[3:])
				return die[0:3]
			else:
				for _ in range(rolls):
					indivroll = random.randint(1, limit)
					res.append(indivroll)
				die.append(res)

				nextroll = sum(1 for i in res if i == limit) #extra number of explosion

				die[0] = attempt + 1
				die[1] = nextroll

				if die[1] == 0 or die[0] >= 20: #depth set to 20. Prevent infinite loop for d1! 
					flat = flatten(die[3:]) 
					newdie = [die[0], die[1], die[2], flat]
					return newdie
				else:
					return evalexpl(die)

		except Exception as e:
			print(e)
			print("Dice must have at least 1 side. \n")

	dexp = makedie(dice) 
	parsedie(dexp) #updates diceexp and actualdie
	finaldie = evalattrib(diceexp) #gives final state of die after attributes applied
	result = list(map(str, finaldie[3]))
	reduced = "(" + functools.reduce(lambda x, y : x + " + " + y, result) + ")"
	return reduced

inp = input("""Dice Roller by Citronella
Example rolls:
3d6    - roll three 6-sided dice, add the results
4d8k2  - roll four 8-sided dice, take the highest 2 results and add them.
4d8l2  - roll four 8-sided dice, take the lowest 2 results and add them.
5d4!   - roll five 4-sided dice, roll again if you get 4; all rolled values are summed.
5*2    - you can do math :D
7d20+3 - you can do math with dice too! \n""")
lst = list(map(evaldice, parse(inp)))
raw = functools.reduce(lambda x, y : x + " " + y, lst)
res = eval(raw)
print("{}: {} = {}".format(inp, raw, res))