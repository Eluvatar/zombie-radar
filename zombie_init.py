#   Copyright (C) 2013-2014 Eluvatar
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Module to download and parse nations.xml for nation names and populations
for a selected list of nations.
"""

from ns import id_str
from parser.client import trawler
from parser import api

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError as PE
import itertools as IT
from time import struct_time, strftime
import gzip

try:
    import progressbar
except ImportError:
    progressbar = False

def initialize_nations(nations):
     trawler.user_agent = api.user_agent
     res = trawler.request('GET', '/pages/nations.xml.gz', headers=True)
     if res.result != 200:
         raise Exception("Error {0}!".format(xf.result))
     _ts = res.info().getdate('Last-Modified')
     dump_ts = struct_time(_ts)
     print "nations.xml date: {0} GMT".format(strftime('%Y-%m-%d %H:%M:%S', dump_ts))
     
     dump_size = int(res.headers['content-length'])

     xf = gzip.GzipFile(fileobj=res)
     context = ET.iterparse(xf, events=('start','end'))
     ic = iter(context)
     db = dict()
  
     if progressbar:
         pb = progressbar.ProgressBar(maxval=dump_size).start()
     else:
         print "printing a . for every 100 nations processed (of about 100,000)"
         i = 0
      
     try: 
         event, root = ic.next()
         for event, elem in ic:
             if elem.tag == 'NATION' and event == 'end':
		 if progressbar:
                     pb.update(res.tell())
                 else:
                     if i%100 == 0:
                         print ".",
                     i += 1
                 cs_name = elem.find('NAME').text
                 nat = id_str(cs_name)
                 if nat in nations:
                     db[nat] = _init_nation(elem, dump_ts, cs_name)
                 root.clear() 
     except PE as e:
         lineno, column = e.position
         xf.seek(0)
         line = next(IT.islice(xf, lineno))
         caret = '{:=>{}}'.format("^", column)
         print ''
         print line
         print caret
         print "i = {0}".format(i)
         raise
     except:
         print ''
         print "i = {0}".format(i)
         raise
     print ''
     # handle new nations
     new_nations = nations - frozenset(db.keys())
     for nat in new_nations:
         db[nat] = init_nation(nat)
     return db

def init_nation(nat):
     elem = api.request({'nation':nat,'q':['name','population']})
     ts = struct_time(elem.headers.getdate('Date'))
     return _init_nation(elem, ts)

def _init_nation(elem, dump_ts, cs_name=None):
     if cs_name == None:
         cs_name = elem.find('NAME').text
     pop = int(elem.find('POPULATION').text)
     entry = dict()
     entry["name"] = cs_name
     entry["ts"] = dump_ts
     entry["action"] = None
     entry["zombies"] = int(pop * 0.08)
     entry["survivors"] = pop - int(pop * 0.08)
     entry["dead"] = 0
     return entry
