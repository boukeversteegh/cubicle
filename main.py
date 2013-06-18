import tornado.ioloop
import tornado.web
import tornado.websocket
from collections import defaultdict
import json
import os
import random
import time
import eventhandler
from multiprocessing import Manager

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("Hello, world")


class Sheet:

	def __init__(self, sheetid):
		self.title	= "Untitled"
		self.cells	= defaultdict(lambda:defaultdict())
		self.width	= 8
		self.height	= 20
		self.sheetid= -1

		self.sheetid=sheetid

	def set(self, x, y, value):
		x=int(x)
		y=int(y)
		self.width	= max(x+1, self.width)
		self.height	= max(y+1, self.height)
		self.cells[y][x] = value

	def get(self, x, y):
		return self.cells[y].get(x, "")

class SheetHandler(tornado.web.RequestHandler):
	def initialize(self, sheets, eventhandler):
		self.sheets = sheets
		self.events = eventhandler

	def _getsheet(self, sheetid):
		#if sheetid not in self.sheets:
		#	self.sheets[sheetid] = Sheet(sheetid=sheetid)
		#return self.sheets[sheetid]
		return self.sheets.setdefault(sheetid, Sheet(sheetid=sheetid))

	def get(self, sheetid):
		sheet = self._getsheet(sheetid)
		self.render('sheets/tpl/sheet.html', sheet=sheet)

	def post(self, sheetid):
		sheet = self._getsheet(sheetid)
		#self.write(json.dumps(kwargs))
		a = self.get_argument('a')

		if a == 'c':
			# Cell update
			x = int(self.get_argument('x'))
			y = int(self.get_argument('y'))
			try:
				v = self.get_argument('v')
			except:
				v = ""
			sheet.set(x=x,y=y, value=v)
			self.events.trigger('update', **{"sheet": sheet, "a":a, "x":x, "y":y, "v":v})
		elif a == 't':
			# Title update
			title = self.get_argument('t')
			sheet.title = title
			self.events.trigger('update', **{"sheet": sheet, "a":a, "t": title})

		time.sleep(0.5)

class SheetWebsocketHandler(tornado.websocket.WebSocketHandler):
	def initialize(self, sheets, eventhandler):
		self.sheets = sheets
		self.events = eventhandler
		def cb_update(sheet, **kwargs):
			if self.sheetid == sheet.sheetid:
				self.write_message(json.dumps(kwargs))

		self.binding = self.events.bind('update', cb_update)

	def open(self):
		print 'new connection'
		self.write_message(json.dumps({"a":"m", "m":"Welcome!"}))
	
	def on_message(self, message):
		print 'message received %s' % message
		data = json.loads(message)
		print repr(data)
		if data['a'] == 'listen':
			self.sheetid = data['sheetid']
 
	def on_close(self):
	  print 'connection closed'
	  self.events.unbind(self.binding)

settings = {
	"static_path": os.path.join(os.path.dirname(__file__), "www"),
	"debug": True
}


sheets = {}#Manager().dict()
eventhandler = eventhandler.EventHandler()
application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/sheet/([a-zA-Z0-9]+)", SheetHandler, dict(sheets=sheets, eventhandler=eventhandler)),
	(r"/ws/sheet", SheetWebsocketHandler, dict(sheets=sheets, eventhandler=eventhandler)),
	(r"/www/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path']))
	],
	**settings
)

if __name__ == "__main__":
	application.listen(8888)
	tornado.ioloop.IOLoop.instance().start()
