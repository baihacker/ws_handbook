import os
import sys
import shutil

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import soj_util

def load_sol(file):
  sol = {}
  sol["count"] = 0
  sol["solutions"] = []
  if os.path.exists(file):
    with open(file, 'r') as tempf:
      sol = eval(tempf.read())
  return sol

    
def save_sol(sol, file):
  data = ['{']
  
  data.append('"count" : %d,'%len(sol["solutions"]))
  
  data.append('"solutions" : [')
  solutions = sorted(sol["solutions"], key = lambda x: int(x["id"]))
  for x in solutions:
    t = []
    t.append('{')
    t.append('"id" : "%s", "title" : "%s",'%(x["id"], x["title"].replace('"', '\\"')))
    t.append('"ctag" : "%s",'%x["ctag"].replace('"', '\\"'))
    t.append('"etag" : "%s",'%x["etag"].replace('"', '\\"'))
    t.append('"brief_solution" : "%s",'%x["brief_solution"].replace('"', '\\"'))
    t.append('},')
    data.extend(t)
  
  data.append(']')
  data.append('}')
  
  with open(file, 'w') as tempf:
    tempf.write('\n'.join(data))

def make_empty_sol(file):
  db = soj_util.load_db("soj_problems.json")
  solved = soj_util.get_solved("baihacker")
  sol = load_sol("")
  solutions = []
  for id in solved:
    if not id in db["index"]: continue
    dic = {}
    dic["id"] = id
    dic["title"] = db["index"][id]
    dic["ctag"] = ""
    dic["etag"] = ""
    dic["brief_solution"] = ""
    solutions.append(dic)
  sol["solutions"] = solutions
  save_sol(sol, file)

if __name__ == "__main__":
  sol = load_sol("soj_solutions.json")
  print(len(sol["solutions"]))