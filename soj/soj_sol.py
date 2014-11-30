#-*- coding: utf8 -*-
import os
import sys
import shutil

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import soj_pdb

def load_sol(file):
  sol = {}
  sol["count"] = 0
  sol["solutions"] = []
  if os.path.exists(file):
    with open(file, 'rb') as tempf:
      sol = eval(tempf.read().decode(encoding='utf8',errors='ignore'))
  return sol

def save_sol(sol, file):
  data = ['{']
  
  data.append('"count" : %d,'%len(sol["solutions"]))
  
  data.append('"solutions" : [')
  solutions = sorted(sol["solutions"], key = lambda x: int(x["id"]))
  for x in solutions:
    t = []
    t.append('{')
    t.append('"id" : "%s", "title" : \"\"\"%s\"\"\",'%(x["id"], x["title"]))
    t.append('"ctag" : "%s",'%x["ctag"])
    t.append('"etag" : "%s",'%x["etag"])
    t.append('"brief_solution" : \"\"\"%s\"\"\",'%x["brief_solution"])
    t.append('},')
    data.extend(t)
  
  data.append(']')
  data.append('}')
  
  with open(file, 'wb') as tempf:
    tempf.write('\r\n'.join(data).encode(encoding='utf8',errors='ignore'))

def make_empty_sol(file):
  db = soj_pdb.load_db("soj_problems.json")
  solved = soj_pdb.get_solved("baihacker")
  sol = load_sol("")
  solutions = []
  for id in solved:
    if not id in db["problems"]: continue
    dic = {}
    dic["id"] = id
    dic["title"] = db["problems"][id]["title"]
    dic["ctag"] = ""
    dic["etag"] = ""
    dic["brief_solution"] = ""
    solutions.append(dic)
  sol["solutions"] = solutions
  save_sol(sol, file)

if __name__ == "__main__":
  #make_empty_sol("soj_solutions.json")
  sol = load_sol("soj_solutions.json")
  #save_sol(sol, "soj_solutions.json")
  print(len(sol["solutions"]))