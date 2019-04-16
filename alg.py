from networkx import *
from networkx.algorithms.matching import max_weight_matching
from pymongo import MongoClient

class Student:
	def __init__(self, name, share_langs, learn_langs, prev_part, denied, creative, flexible, major, partner):
		self.name = name
		self.share_langs = share_langs
		self.learn_langs = learn_langs
		self.prev_part = prev_part
		self.denied = denied
		self.creative = creative
		self.flexible = flexible
		self.partner = partner
		self.major = major

class Pair:
	def __init__(self, student1, student2):
		self.student1 = student1
		self.student2 = student2
		langs = canMatch(student1, student2) #the languages they will exchange
		self.language1 = langs[0]
		self.language2 = langs[1]
		self.prof1 = makeProfs(student1, langs)
		self.prof2 = makeProfs(student2, langs)

stemCluster = ['Genetics', 'Statistics', 'Microbiology', 'Geology', 'Ecology', 'Biological Sciences', 'Exercise Science', 'Cognitive Science', 'Computer Science', 'Mathematics', 'Physics', 'Biology', 'Chemistry', 'Chemical Engineering', 'Materials Science', 'Aerospace Engineering', 'Mechanical Engineering', 'Electrical Engineering', 'Environmental Engineering', 'Biomedical Engineering', 'Civil Engineering']
humanitiesCluster = ['Philosophy', 'Religion', 'Russian', 'Journalism', 'English', 'Chinese', 'Korean', 'Classics', 'Comparitive Literature', 'French', 'Cultural French', 'German', 'Spanish', 'Italian', 'Japanese', 'Portuguese', 'History', 'Law', 'European Studies', 'Middle Eastern Studies', 'Medieval Studies', 'American Studies', 'Jewish Studies', 'Italian Studies', 'German Studies']
businessCluster = ['Economics', 'BAIT', 'Accounting', 'Finance', 'Marketing', 'Human Resource Management', 'Supply Chain Management']
artsCluster = ['Dance', 'Art', 'Music', 'Theater', 'Art History', 'Cinema Studies']
socialScienceCluster = ['Criminal Justice', 'Cognitive Science', 'Linguistics', 'Communication', 'Sociology', 'Geography', 'Anthropology', 'Political Science']

def makeProfs(student, langs):
	result = ""
	if langs[0] in student.learn_langs:
		result = result + langs[0] + ": " + student.learn_langs.get(langs[0]) + " & "
	else: 
		result = result + langs[0] + ": " + student.share_langs.get(langs[0]) + " & "
	if langs[1] in student.learn_langs:
		result = result + langs[1] + ": " + student.learn_langs.get(langs[1])
	else: 
		result = result + langs[1] + ": " + student.share_langs.get(langs[1])
	return result

def canMatch(s, ss): #checks if two students can share/learn from each other
	langs = [] 
	for l in s.learn_langs:
		if l != 'None' and canLearn(s, l) and canShare(ss, l) and not bothAreFluent(s, ss, l):
			for j in ss.learn_langs:
				if j != l and j != 'None' and canLearn(ss, j) and canShare(s, j) and not bothAreFluent(s, ss, j):
					langs.append(j)
					langs.append(l)
	return langs

def canLearn(s, lang):
	return (lang in s.learn_langs and lang != 'None')

def canShare(s, lang):
	return (lang in s.share_langs and (s.share_langs.get(lang) == 'fluent' or s.share_langs.get(lang) == 'advanced'))

def bothAreFluent(s, ss, lang):
	return ((s.share_langs.get(lang) == 'fluent' or s.learn_langs.get(lang) == 'fluent') and (ss.share_langs.get(lang) == 'fluent' or ss.learn_langs.get(lang) == 'fluent'))

def weight(s, ss): 
	#start at 0
	weight = 0
	common_langs = canMatch(s, ss)

	for language in common_langs:
		#if 1st choice += 75, if 2nd choice +37
		if(list(s.share_langs)[0] == language):
			weight += 75
		elif(len(list(s.share_langs)) > 1 and list(s.share_langs)[1] == language):
			weight += 37
		if(list(ss.share_langs)[0] == language):
			weight += 75
		elif(len(list(ss.share_langs)) > 1 and list(ss.share_langs)[1] == language):
			weight += 37
		if(list(s.learn_langs)[0] == language):
			weight += 75
		elif(len(list(s.learn_langs)) > 1 and list(s.learn_langs)[1] == language):
			weight += 37
		if(list(ss.learn_langs)[0] == language):
			weight += 75
		elif(len(list(ss.learn_langs)) > 1 and list(ss.learn_langs)[1] == language):
			weight += 37

	#bonus for being denied or not previously participating
	if(s.denied == 'unable'):
		weight += 350
	elif(s.prev_part == 'did_not'):
		weight += 125
	if(ss.denied == 'unable'):
		weight += 350
	elif(ss.prev_part == 'did_not'):
		weight += 125

	rate1diff = abs(int(s.creative) - int(ss.creative))
	if rate1diff == 0:
		weight += 49
	elif rate1diff == 1:
		weight += 39
	elif rate1diff == 2:
		weight += 26
	elif rate1diff == 3:
		weight += 13

	rate2diff = abs(int(s.flexible) - int(ss.flexible))
	if rate2diff == 0:
		weight += 49
	elif rate2diff == 1:
		weight += 39
	elif rate2diff == 2:
		weight += 26
	elif rate2diff == 3:
		weight += 13

	#+10 for majors in the same cluster
	if(s.major in stemCluster and ss.major in stemCluster):
		weight += 10
	elif(s.major in businessCluster and ss.major in businessCluster):
		weight += 10
	elif(s.major in artsCluster and ss.major in artsCluster):
		weight += 10
	elif(s.major in humanitiesCluster and ss.major in humanitiesCluster):
		weight += 10
	elif(s.major in socialScienceCluster and ss.major in socialScienceCluster):
		weight += 10

	return round((weight / 1108), 4) + 3

def make_pairs():
	#creates connection to mongodb database
	client = MongoClient("mongodb+srv://admin:rutgers1@studentinfo-eoita.azure.mongodb.net/test?retryWrites=true")
	db = client.test
	
	rows = db.inventory.find({'partner':'None'})

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
	    students.append(Student(row['name'], share_langs, learn_langs, row['prevp'], row['unableprev'], row['rate1'], row['rate2'], row['majors'], row['partner']))

	G = Graph()

	#adds students who can potentially be partners to the graph
	for s in students:
		for ss in students:
			l = canMatch(s, ss)
			if(s != ss and len(l) != 0):
				G.add_edge(s, ss, weight=weight(s, ss))
				#print(s.name + " and " + ss.name + " for " + canMatch(s, ss)[0] + " and " + canMatch(s, ss)[1] + " (" + str(weight(s, ss)) + ") ")

	#s = sorted(max_weight_matching(G))
	#print('{' + ', '.join(map(lambda t: ': '.join(map(repr, t)), s)) + '}')
	
	pairset = max_weight_matching(G, maxcardinality=True) #result of max weighting algorithm 
	pairs = []
	for p in pairset:
		pairs.append(Pair(p[0], p[1]))
	return pairs

pairs = make_pairs()
for p in pairs:
	print(p.student1.name + " & " + p.student2.name)
	print(p.language1 + " & " + p.language2)
print(len(pairs))
