from pymongo import MongoClient

import plotly as py
import plotly.graph_objs as go


client = MongoClient("mongodb+srv://admin:rutgers1@studentinfo-eoita.azure.mongodb.net/test?retryWrites=true")
db = client.test



def gen_learn_pie():
	rows = db.inventory.find({})
	d = {}
	for r in rows:
		for l in ['ll1', 'll2', 'll3']:
			if(r[l] != 'None'):
				if (r[l] in d.keys()):
					d[r[l]] = d.get(r[l]) + 1
				else:
					d[r[l]] = 1

	data = [go.Pie(
	            labels= list(d.keys()),
	            values= list(d.values())
	    )]

	py.offline.plot({
	    "data": data,
	    "layout": go.Layout(title="Languages People Want To Learn")
	}, filename='templates/learn-count-pie.html', auto_open=False)
	print('plot made')


def gen_share_pie():
	rows = db.inventory.find({})
	d2 = {}

	for r in rows:
		for l in ['sl1', 'sl2', 'sl3']:
			if(r[l] != 'None'):
				if (r[l] in d2.keys()):
					d2[r[l]] = d2.get(r[l]) + 1
				else:
					d2[r[l]] = 1

	data = [go.Pie(
	            labels= list(d2.keys()),
	            values= list(d2.values())
	    )]

	py.offline.plot({
	    "data": data,
	    "layout": go.Layout(title="Languages People Want To Share")
	}, filename='templates/share-count-pie.html', auto_open=False)
