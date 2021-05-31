#-*- coding: utf8 -*-
import urllib
import urllib.request
import re
import time
import os
import socket

socket.setdefaulttimeout(20)

run_on_server = True
run_on_local = not run_on_server
mc = None

soj_prefix = 'http://acm.scu.edu.cn'


# memcache
def memcache_client():
  global mc
  if mc != None:
    return mc

  try:
    memcache = __import__('memcache')
    mc = memcache.Client(['127.0.0.1:12345'], debug=0)
    return mc
  except:
    return None


def cached_get(key, para, get_data):
  if run_on_local:
    return get_data(para)
  memcache_client()
  if mc != None:
    result = mc.get(key)
    if result != None:
      return result
  result = get_data(para)
  if result != None:
    if mc != None:
      mc.set(key, result, time=60 * 60 * 24)
  return result


def load_file_data(file, key=None):

  def read_file_data(f):
    if os.path.exists(f):
      with open(f, 'rb') as tempf:
        result = tempf.read()
        return result
    else:
      return None

  if key == None:
    return read_file_data(file)
  else:
    return cached_get(key, file, read_file_data)


def load_db(file, key=None):
  db = {}
  db["count"] = 0
  db["enabled"] = 0
  db["checked_page"] = []
  db["problems"] = {}
  db["last_update"] = 0.0
  text = load_file_data(file, key)
  if text != None:
    db = eval(text.decode(encoding='utf8', errors='ignore'))
    db["problems"] = {item["id"]: item for item in db["problems"]}
  return db


def save_db(db, file):
  data = ['{']

  data.append('"count" : %d,' % len(db["problems"]))

  t = '"checked_page" : [' % db["checked_page"]
  for x in db["checked_page"]:
    t += "%d," % x
  t += '],'
  data.append(t)

  enabled = 0
  zero_ac = 0

  data.append('"problems" : [')
  temp = sorted([x for x in db["problems"].items()], key=lambda x: int(x[0]))
  for x in temp:
    detail = x[1]
    now = '{'
    now += '"id" : "%s", ' % x[0]
    now += '"title" : \"\"\"%s\"\"\", ' % detail["title"]
    now += '"submit" : %d, ' % detail["submit"]
    now += '"solved" : %d, ' % detail["solved"]
    if "enable" in detail:
      now += '"enable" : %d, ' % detail["enable"]
      enabled += detail["enable"]
      if detail["enable"] > 0 and detail["solved"] == 0:
        zero_ac += 1
    now += '},'
    data.append(now)

  data.insert(2, '"enabled" : %d,' % enabled)
  data.insert(3, '"zero_ac" : %d,' % zero_ac)
  data.insert(4, '"last_update" : %f,' % time.time())

  data.append(']')
  data.append('}')

  with open(file, 'wb') as tempf:
    tempf.write('\r\n'.join(data).encode(encoding='utf8', errors='ignore'))


def get_user_solved(user_id):

  def get_user_solved_html_from_web(id):
    url = "%s/soj/user.action?id=%s" % (soj_prefix, urllib.parse.quote(id))
    f = urllib.request.urlopen(url)
    result = f.read().decode(encoding='gbk',
                             errors='ignore').encode(encoding='utf8',
                                                     errors='ignore')
    return result

  result = cached_get(user_id, user_id,
                      get_user_solved_html_from_web).decode(encoding='utf8',
                                                            errors='ignore')
  items = re.findall(r'<a href="problem.action\?id=\d+">\d+</a>', result)
  return set([item[-8:-4] for item in items])


def load_sol(file, key=None):
  sol = {}
  sol["count"] = 0
  sol["solutions"] = []
  text = load_file_data(file, key)
  if text != None:
    sol = eval(text.decode(encoding='utf8', errors='ignore'))
  return sol


def save_sol(sol, file):
  data = ['{']

  data.append('"count" : %d,' % len(sol["solutions"]))

  data.append('"solutions" : [')
  solutions = sorted(sol["solutions"], key=lambda x: int(x["id"]))
  for x in solutions:
    t = []
    t.append('{')
    t.append('"id" : "%s", "title" : \"\"\"%s\"\"\",' % (x["id"], x["title"]))
    t.append('"ctag" : "%s",' % x["ctag"])
    t.append('"etag" : "%s",' % x["etag"])
    t.append('"brief_solution" : \"\"\"%s\"\"\",' % x["brief_solution"])
    t.append('},')
    data.extend(t)

  data.append(']')
  data.append('}')

  with open(file, 'wb') as tempf:
    tempf.write('\r\n'.join(data).encode(encoding='utf8', errors='ignore'))
