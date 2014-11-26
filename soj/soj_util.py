import urllib
import urllib.request
import re
import time
import os

def get_problems(page):
  url = "http://cstest.scu.edu.cn/soj/problems.action?volume=%d"%page
  f = urllib.request.urlopen(url)
  result = f.read().decode(encoding='gbk',errors='ignore')
  items = re.findall('<a href="problem.action\\?id=\\d+">.*?</a></td>', result)
  result = []
  for iter in items:
    result.append((iter[27:31], iter[33:-9]))
  return result

def load_db(file):
  db = {}
  db["count"] = 0
  db["checked_page"] = []
  db["problems"] = []
  if os.path.exists(file):
    with open(file, 'r') as tempf:
      db = eval(tempf.read())
  db["index"] = {item[0]:item[1] for item in db["problems"]}
  return db

def save_db(db, file):
  data = ['{']
  
  data.append('"count" : %d,'%len(db["problems"]))
  
  t = '"checked_page" : ['%db["checked_page"]
  for x in db["checked_page"]:
    t += "%d,"%x
  t += '],'
  data.append(t)
  
  data.append('"problems" : [')
  db["problems"] = sorted(db["problems"], key = lambda x: int(x[0]))
  for x in db["problems"]:
    now = '('
    now += '"%s", '%x[0]
    now += '"%s"),'%x[1].replace('"', '\\"')
    data.append(now)
  
  data.append(']')
  data.append('}')
  
  with open(file, 'w') as tempf:
    tempf.write('\n'.join(data))

def insert_item(db, item):
  if not item[0] in db["index"]:
    db["problems"].append(item)
    db["index"][item[0]] = item[1]

def update_db(file):
  db = load_db(file)
  for page in range(0, 33):
    if page in db["checked_page"]: continue
    problems = get_problems(page)
    for item in problems: insert_item(db, item)
    db["checked_page"].append(page)
    save_db(db, file)

def get_solved(id):
  url = "http://cstest.scu.edu.cn/soj/user.action?id=%s"%urllib.parse.quote(id, encoding="gbk")
  f = urllib.request.urlopen(url)
  result = f.read().decode(encoding='gbk',errors='ignore')
  items = re.findall('<a href="problem.action\\?id=\\d+">\\d+</a>', result)
  return set([item[-8:-4] for item in items])

if __name__ == "__main__":
  update_db("soj_problems.json")