#-*- coding: utf8 -*-
import soj_db
import re
import urllib
import urllib.request


def make_empty_sol(file):
  db = soj_db.oad_db("soj_problems.json")
  solved = soj_db.get_solved("baihacker")
  sol = soj_db.load_sol("")
  solutions = []
  for id in solved:
    if not id in db["problems"]:
      continue
    dic = {}
    dic["id"] = id
    dic["title"] = db["problems"][id]["title"]
    dic["ctag"] = ""
    dic["etag"] = ""
    dic["brief_solution"] = ""
    solutions.append(dic)
  sol["solutions"] = solutions
  soj_db.save_sol(sol, file)


def insert_problem(db, item):
  if not item[0] in db["problems"]:
    db["problems"][item[0]] = item[1]
  else:
    db["problems"][item[0]]['submit'] = item[1]['submit']
    db["problems"][item[0]]['solved'] = item[1]['solved']


def get_problems(page):
  url = "%s/soj/problems.action?volume=%d" % (soj_db.soj_prefix, page)
  f = urllib.request.urlopen(url)
  text = f.read().decode(encoding='gbk', errors='ignore')

  p_problem = re.compile(
      r'<a href="problem.action\?id=\d+">.*?</a></td>.*?<td align="right">\d+</td>.*?<td align="right"><a href="problem_best_solutions.action\?id=\d+">\d+</a></td>',
      re.S)

  items = p_problem.findall(text)

  p_id_title = re.compile(r'<a href="problem.action\?id=\d+">.*?</a></td>')
  p_submit = re.compile(r'<td align="right">\d+</td>')
  p_solved = re.compile(
      r'<td align="right"><a href="problem_best_solutions.action\?id=\d+">\d+</a></td>'
  )

  ret = []
  for iter in items:
    a0 = p_id_title.findall(iter)
    a1 = p_submit.findall(iter)
    a2 = p_solved.findall(iter)
    if len(a0) != 1 or len(a1) != 1 or len(a2) != 1:
      print("warning : search failed at string\n%s" % iter)
      continue
    t = {}
    t["id"] = a0[0][27:31]
    t["title"] = a0[0][33:-9]
    t["submit"] = int(a1[0][18:-5])
    t["solved"] = int(a2[0][66:-9])
    ret.append((a0[0][27:31], t))

  return ret


def update_problem_list(file):
  db = soj_db.load_db(file)
  for page in range(0, 38):
    if page in db["checked_page"]:
      continue
    problems = get_problems(page)
    for item in problems:
      insert_problem(db, item)
    db["checked_page"].append(page)
    soj_db.save_db(db, file)


def update_enable_state(file):
  db = soj_db.load_db(file)
  p_submit = re.compile(
      r'<a href="submit_form.action\?id=\d+">Submit your solution</a>')
  for k, v in db["problems"].items():
    if "enable" in v:
      continue
    url = "%s/soj/problem.action?id=%s" % (soj_db.soj_prefix, k)
    f = urllib.request.urlopen(url)
    text = f.read().decode(encoding='gbk', errors='ignore')
    exist = p_submit.findall(text)
    print("update enable state : %s" % k)
    v["enable"] = 1 if len(exist) > 0 else 0
    soj_db.save_db(db, file)


if __name__ == "__main__":
  update_problem_list("soj_problems.json")
  update_enable_state("soj_problems.json")
  db = soj_db.load_db("soj_problems.json")
  soj_db.save_db(db, "soj_problems.json")
  #sol = soj_db.load_sol("soj_solutions.json")
  #print(len(sol["solutions"]))
  #print(soj_db.get_user_solved('baihacker'))