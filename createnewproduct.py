import sublime, sublime_plugin, os
from ftplib import FTP
from random import randint
import http.client
import urllib.parse


# fix DATE

class promptcreatenewproductCommand(sublime_plugin.WindowCommand):
	def run(self):

		self.window.show_input_panel("Create New Product| Enter ProductID:","Product1",self.pid_done,None,None)

	def pid_done(self, data):
		self.pid = data
		self.get_clientname()

	def get_clientname(self):
		self.window.show_input_panel("Create New Product| Enter Client:","smb-demo",self.clientname_done,None,None)

	def clientname_done(self, data):
		self.clientname = data
		self.get_imageURL()

	def get_imageURL(self):
		self.window.show_input_panel("Create New Product| Enter Image URL:","http://placehold.it/500X500",self.imageURL_done,None,None)

	def imageURL_done(self, data):
		self.imageURL = data
		self.get_pname()

	def get_pname(self):
		self.window.show_input_panel("Create New Product| Enter Product Name:","Red Stapler",self.pname_done,None,None)

	def pname_done(self, data):
		self.pname = data
		self.get_ptype()

	def get_ptype(self):
		self.window.show_input_panel("Review Template (Electronics[1], Health & Beauty[2], CPG[3], Hotels[4], Finserv[5], Appliance[6], Outdoors[7]","Electronics",self.ptype_done,None,None)

	def ptype_done(self, data):
		self.ptype = data
		self.cnp_continue()
		
	def cnp_continue(self):
		self.window.run_command("createfile",{ "clientname": self.clientname, "externalid": self.pid, "productname": self.pname, "imageurl": self.imageURL, "ptype": self.ptype} )

class createfileCommand(sublime_plugin.WindowCommand):
	def run(self, clientname, externalid, productname, imageurl, ptype):
		
		templatexml = '<?xml version="1.0" encoding="UTF-8"?><Feed xmlns="http://www.bazaarvoice.com/xs/PRR/ProductFeed/5.6" name="$CLIENTNAME$" incremental="true" extractDate="$DATE$"><Brands><Brand><ExternalId>brand1</ExternalId><Name>Brand</Name></Brand></Brands><Categories><Category><ExternalId>1</ExternalId><Name>Electronics</Name><CategoryPageUrl>http://brandbox.droppages.com/Products</CategoryPageUrl></Category></Categories><Products><Product><ExternalId>$EXTERNALID$</ExternalId><BrandExternalId>brand1</BrandExternalId><CategoryExternalId>1</CategoryExternalId><Name>$PRODUCTNAME$</Name><Description>Example Description</Description><ProductPageUrl>http://example.com/product1</ProductPageUrl><ImageUrl>$IMAGEURL$</ImageUrl></Product></Products></Feed>'

		templatexml = templatexml.replace("$DATE$", '2013-01-01T12:00:00.000000')
		templatexml = templatexml.replace("$CLIENTNAME$",clientname)
		templatexml = templatexml.replace("$EXTERNALID$",externalid)
		templatexml = templatexml.replace("$PRODUCTNAME$",productname)
		templatexml = templatexml.replace("$IMAGEURL$",imageurl)

		filename = "bvintegratorproductfeed"+str(randint(0,999999))+".xml" 
		f = open(filename,"w+")
		f.write(templatexml)
		f.close()
		

		ftp = FTP(host='ftp-stg.bazaarvoice.com')
		ftp.login('smb-demo','aVGe8&wG138K')
		ftp.cwd('import-inbox')
		ftp.storlines("STOR " + filename, open(filename,"rb"))
		f.close()

		self.window.run_command("submitreviews",{ "clientname": clientname, "externalid": externalid, "productname": productname, "imageurl": imageurl, "ptype": ptype} )


class submitreviewsCommand(sublime_plugin.WindowCommand):
	def run(self, clientname, externalid, productname, imageurl, ptype):


		reviews = [["Great!","Wow! I love my "+productname+". This is my favorite!","johnny"+str(randint(0,9999)) ],["The Best","This "+productname+" is really the best. I just love it.","nicki"+str(randint(0,9999))],["WOW","All I can say is WOW. I bought the "+productname+" last month and am loving it","mario"+str(randint(0,9999))]]

		for x in reviews:
			params = urllib.parse.urlencode({
				'ApiVersion' : '5.4',
				'ProductId' : externalid,
				'Action' : 'Submit',
				'Rating' : '5',
				'ReviewText' : x[1],
				'Title' : x[0],
				'UserNickname' : x[2],
				'PassKey' : 's5pfp4r4tgdurx257axt9z3a'
    		})

			headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
			connection = http.client.HTTPConnection("stg.api.bazaarvoice.com:80")
			connection.request("POST", "/data/submitreview.json", params, headers)
			response = connection.getresponse()
			print (response.status, response.reason)
			connection.close()


			









