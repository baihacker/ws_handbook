#-*- coding: utf8 -*-
import urllib
import urllib.request
import re
import time
import os

def get_problems(page):
  url = "http://acm.scu.edu.cn/soj/problems.action?volume=%d"%page
  f = urllib.request.urlopen(url)
  text = f.read().decode(encoding='gbk',errors='ignore')

  p_problem = re.compile(r'<a href="problem.action\?id=\d+">.*?</a></td>.*?<td align="right">\d+</td>.*?<td align="right"><a href="problem_best_solutions.action\?id=\d+">\d+</a></td>', re.S)

  items = p_problem.findall(text)

  p_id_title = re.compile(r'<a href="problem.action\?id=\d+">.*?</a></td>')
  p_submit = re.compile(r'<td align="right">\d+</td>')
  p_solved = re.compile(r'<td align="right"><a href="problem_best_solutions.action\?id=\d+">\d+</a></td>')
  
  ret = []
  for iter in items:
    a0 = p_id_title.findall(iter)
    a1 = p_submit.findall(iter)
    a2 = p_solved.findall(iter)
    if len(a0) != 1 or len(a1) != 1 or len(a2) != 1:
      print("warning : search failed at string\n%s"%iter)
      continue
    t = {}
    t["id"] = a0[0][27:31]
    t["title"] = a0[0][33:-9]
    t["submit"] = int(a1[0][18:-5])
    t["solved"] = int(a2[0][66:-9])
    ret.append((a0[0][27:31], t))

  return ret

def load_db(file):
  db = {}
  db["count"] = 0
  db["enabled"] = 0
  db["checked_page"] = []
  db["problems"] = {}
  db["last_update"] = 0.0
  if os.path.exists(file):
    with open(file, 'rb') as tempf:
      db = eval(tempf.read().decode(encoding='utf8',errors='ignore'))
      db["problems"] = {item["id"]:item for item in db["problems"]}
  return db

def save_db(db, file):
  data = ['{']
  
  data.append('"count" : %d,'%len(db["problems"]))
  
  t = '"checked_page" : ['%db["checked_page"]
  for x in db["checked_page"]:
    t += "%d,"%x
  t += '],'
  data.append(t)
  
  enabled = 0
  zero_ac = 0
  
  data.append('"problems" : [')
  temp = sorted([x for x in db["problems"].items()], key = lambda x: int(x[0]))
  for x in temp:
    detail = x[1]
    now = '{'
    now += '"id" : "%s", '%x[0]
    now += '"title" : \"\"\"%s\"\"\", '%detail["title"]
    now += '"submit" : %d, '%detail["submit"]
    now += '"solved" : %d, '%detail["solved"]
    if "enable" in detail:
      now += '"enable" : %d, '%detail["enable"]
      enabled += detail["enable"]
      if detail["enable"] > 0 and detail["solved"] == 0:
        zero_ac += 1
    now += '},'
    data.append(now)
  
  data.insert(2, '"enabled" : %d,'%enabled)
  data.insert(3, '"zero_ac" : %d,'%zero_ac)
  data.insert(4, '"last_update" : %f,'%time.time())
  
  data.append(']')
  data.append('}')
  
  with open(file, 'wb') as tempf:
    tempf.write('\r\n'.join(data).encode(encoding='utf8',errors='ignore'))

def insert_problem(db, item):
  if not item[0] in db["problems"]:
    db["problems"][item[0]] = item[1]
  else:
    db["problems"][item[0]]['submit'] = item[1]['submit']
    db["problems"][item[0]]['solved'] = item[1]['solved']

def update_problem_list(file):
  db = load_db(file)
  for page in range(0, 34):
    if page in db["checked_page"]: continue
    problems = get_problems(page)
    for item in problems: insert_problem(db, item)
    db["checked_page"].append(page)
    save_db(db, file)

def update_enable_state(file):
  db = load_db(file)
  p_submit = re.compile(r'<a href="submit_form.action\?id=\d+">Submit your solution</a>')
  for k, v in db["problems"].items():
    if "enable" in v: continue
    url = "http://acm.scu.edu.cn/soj/problem.action?id=%s"%k
    f = urllib.request.urlopen(url)
    text = f.read().decode(encoding='gbk',errors='ignore')
    exist = p_submit.findall(text)
    print("update enable state : %s"%k)
    v["enable"] = 1 if len(exist) > 0 else 0
    save_db(db, file)

def get_solved(id):
  url = "http://acm.scu.edu.cn/soj/user.action?id=%s"%urllib.parse.quote(id, encoding='gbk')
  f = urllib.request.urlopen(url)
  result = f.read().decode(encoding='gbk',errors='ignore')
  items = re.findall(r'<a href="problem.action\?id=\d+">\d+</a>', result)
  return set([item[-8:-4] for item in items])

if __name__ == "__main__":
  update_problem_list("soj_problems.json")
  update_enable_state("soj_problems.json")
  db = load_db("soj_problems.json")
  save_db(db, "soj_problems.json")