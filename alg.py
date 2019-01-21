from networkx import *
from networkx.algorithms.matching import max_weight_matching
from pymongo import MongoClient

class Student:
	def __init__(self, name, share_langs, learn_langs, prev_part, partner):
		self.name = name
		self.share_langs = share_langs
		self.learn_langs = learn_langs
		self.prev_part = prev_part
		self.partner = partner

class Pair:
	def __init__(self, student1, student2):
		self.student1 = student1
		self.student2 = student2
		langs = canMatch(student1, student2)
		self.language1 = langs[0]
		self.language2 = langs[1]

def canMatch(s, ss):
	langs = [] 
	for l in s.learn_langs:
		if canLearn(s, l) and canShare(ss, l):
			#print("EDGE MADE BETWEEN " + s.name + " (" + s.learn_langs.get(l) + ") AND " + ss.name + " (" + ss.share_langs.get(l) + ") FOR " + l)
			for j in ss.learn_langs:
				if j != l and canLearn(ss, j) and canShare(s, j):
					#print("EDGE MADE BETWEEN " + s.name + " (" + s.share_langs.get(l) + ") AND " + ss.name + " (" + ss.learn_langs.get(j) + ") FOR " + j + " AND " + l)
					langs.append(j)
					langs.append(l)
	return langs

def canLearn(s, lang):
	return (lang in s.learn_langs and lang != 'None')

def canShare(s, lang):
	return (lang in s.share_langs and s.share_langs.get(lang) == 'fluent' or s.share_langs.get(lang) == 'advanced')

def weight(s, ss):
	total = 1
	if(s.prev_part == 'did_not'):
		total += 2
	if(ss.prev_part == 'did_not'):
		total += 2
	return total

def make_pairs():
	client = MongoClient("mongodb+srv://admin:rutgers1@studentinfo-eoita.azure.mongodb.net/test?retryWrites=true")
	db = client.test

	# db.inventory.update_many(
	# 	{"$or" : [
	# 		{"partner": {"$exists": False}},
	# 		{"partner": None},
	# 	]},
	#    {"$set": {"partner": "None"}}
	# )

	rows = db.inventory.find({})

	students = []

	for row in rows:
	    share_langs = {
	        row['sl1']: row['sp1'],
	        row['sl2']: row['sp2'],
	        row['sl3']: row['sp3']
	    }
	    learn_langs = {
	        row['ll1']: row['lp1'],
	        row['ll2']: row['lp2'],
	        row['ll3']: row['lp3']
	    }
	    students.append(Student(row['name'], share_langs, learn_langs, row['prevp'], row['partner']))

	G = Graph()

	for s in students:
		if(s.partner == 'None'):
			for ss in students:
				if(ss.partner == 'None'):
					l = canMatch(s, ss)
					if(s != ss and len(l) != 0):
						G.add_edge(s, ss, weight=weight(s, ss))

	#s = sorted(max_weight_matching(G))
	#print('{' + ', '.join(map(lambda t: ': '.join(map(repr, t)), s)) + '}')
	pairset = max_weight_matching(G, maxcardinality=False)
	pairs = []
	for p in pairset:
		pairs.append(Pair(p[0], p[1]))
	return pairs


pairs = make_pairs()
for p in pairs:
	print(p.student1.name + " & " + p.student2.name)
	print(p.language1 + " & " + p.language2)