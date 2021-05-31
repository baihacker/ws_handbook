#-*- coding: utf8 -*-
import os
import sys
import shutil
import cgi
import time
import urllib
import html

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import soj_db

CURR_DIR = os.path.dirname(os.path.realpath(__file__))
problems_db_path = os.path.join(CURR_DIR, 'soj_problems.json')
solutions_db_path = os.path.join(CURR_DIR, 'soj_solutions.json')


def safe_get_solved_impl(user):
  try:
    return True, set(soj_db.get_user_solved(user))
  except:
    return False, set()


def safe_get_solved(user):
  for i in range(0, 5):
    OK, ret = safe_get_solved_impl(user)
    if OK:
      return True, ret
    time.sleep(1)
  print('Can not connect to soj!')
  return False, set()


def get_user_info(user):
  ret = {}
  ret['error'] = -1

  # load db
  db = soj_db.load_db(problems_db_path)
  if not 'problems' in db:
    return ret
  problems = db['problems']

  # find solved
  OK, user_solved = safe_get_solved(user)
  if OK != True:
    return ret

  # generate info
  real_solved = []
  real_unsolved = []
  total_score = 0.0
  for (k, v) in problems.items():
    if not 'enable' in v or v['enable'] == 0:
      continue
    id = k
    submit = v['submit']
    solved = v['solved']
    title = v['title']
    ac_ratio = 0. if solved == 0 or submit == 0 else 1. * solved / submit
    if k in user_solved:
      earn = 80. / (39 + solved)
      total_score += earn
      real_solved.append((id, title, submit, solved, ac_ratio, earn))
    else:
      real_unsolved.append((id, title, submit, solved, ac_ratio, 0))
  ret['real_solved'] = real_solved
  ret['real_unsolved'] = real_unsolved
  ret['total_score'] = total_score
  ret['error'] = 0
  return ret


def merge_solved(solved1, solved2):
  both_solved = []
  only_first = []
  only_second = []
  n1 = len(solved1)
  n2 = len(solved2)
  i = 0
  j = 0
  while i < n1 and j < n2:
    if solved1[i][0] == solved2[j][0]:
      both_solved.append(solved1[i])
      i += 1
      j += 1
    elif solved1[i][0] < solved2[j][0]:
      only_first.append(solved1[i])
      i += 1
    else:
      only_second.append(solved2[j])
      j += 1
  while i < n1:
    only_first.append(solved1[i])
    i += 1
  while j < n2:
    only_second.append(solved2[j])
    j += 1
  return both_solved, only_first, only_second


def work_cmd():
  if len(sys.argv) <= 1:
    print('error!')
    return
  cmd = sys.argv[1]
  if cmd == 'perf':
    if len(sys.argv) <= 2:
      print('error!')
      return
    info = get_user_info(sys.argv[2])
    if not 'error' in info or info['error'] != 0:
      print('error!')
      return
    text = []
    text.append('User : %s' % sys.argv[2])
    text.append('Solved : %d' % len(info['real_solved']))
    text.append('Score : %f' % info['total_score'])
    text.append('Progress : %.2f%%' %
                (100. * len(info['real_solved']) /
                 (len(info['real_solved']) + len(info['real_unsolved']))))

    unsolved = info['real_unsolved']
    unsolved = sorted(unsolved, key=lambda x: (-x[3], -x[4], x[0]))
    total = min(16, len(unsolved))
    if total > 0:
      text.append('Top 16 unsolved:')
      for i in range(0, total):
        text.append('%s %s (solved: %d submit: %d ac ratio: %.2f%%)' %
                    (unsolved[i][0], unsolved[i][1], unsolved[i][3],
                     unsolved[i][2], 100 * unsolved[i][4]))

    solved = info['real_solved']
    solved = sorted(solved, key=lambda x: (x[3], x[4], x[0]))
    total = min(16, len(solved))
    if total > 0:
      text.append('Top 16 solved:')
      for i in range(0, total):
        text.append('%s %s (solved: %d submit: %d ac ratio: %.2f%% score: %f)' %
                    (solved[i][0], solved[i][1], solved[i][3], solved[i][2],
                     100 * solved[i][4], solved[i][5]))

    print('\r\n'.join(text))
  elif cmd == 'cmp':
    if len(sys.argv) <= 3:
      print('error!')
      return
    user1, user2 = sys.argv[2], sys.argv[3]
    info1 = get_user_info(user1)
    if not 'error' in info1 or info1['error'] != 0:
      print('error!')
      return
    info2 = get_user_info(user2)
    if not 'error' in info2 or info2['error'] != 0:
      print('error!')
      return
    both, first, second = merge_solved(sorted(info1['real_solved']),
                                       sorted(info2['real_solved']))
    print('only %s solved (%d):' % (user1, len(first)))
    print([x[0] for x in first])
    print('only %s solved (%d):' % (user2, len(second)))
    print([x[0] for x in second])
  else:
    print('unknown cmd')


def work_html():
  if len(sys.argv) <= 1:
    print('error!')
    return
  cmd = sys.argv[1]
  if cmd == 'perf':
    if len(sys.argv) <= 2:
      print('error!')
      return
    user = urllib.parse.unquote(sys.argv[2])
    info = get_user_info(user)
    if not 'error' in info or info['error'] != 0:
      print('error!')
      return
    text = []
    text.append('<table cellpadding="1" border="1" width = "800">')
    text.append('<tr><td>User</td><td align="center">%s</td></tr>' %
                html.escape(user))
    text.append('<tr><td>Solved</td><td align="center">%d</td></tr>' %
                len(info['real_solved']))
    text.append('<tr><td>Score</td><td align="center">%f</td></tr>' %
                info['total_score'])
    text.append('<tr><td>Progress</td><td align="center">%.2f%%</td></tr>' %
                (100. * len(info['real_solved']) /
                 (len(info['real_solved']) + len(info['real_unsolved']))))

    text.append(
        '<tr><td rowspan="4">Problems</td><td align="center">Top 16 unsolved</td></tr>'
    )

    text.append('<tr>')
    unsolved = info['real_unsolved']
    unsolved = sorted(unsolved, key=lambda x: (-x[3], -x[4], x[0]))
    total = min(16, len(unsolved))
    if total > 0:
      text.append('<td valign="top"><table cellpadding="3" width="100%">')
      text.append(
          '<tr><td>Id</td><td>Title</td><td>Accepted</td><td>Submit</td><td>AC Ratio</td></tr>'
      )
      for i in range(0, total):
        text.append(
            '<tr><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%.2f%%</td></tr>'
            % (unsolved[i][0], unsolved[i][1], unsolved[i][3], unsolved[i][2],
               100 * unsolved[i][4]))
      text.append('</table></td>')
    else:
      text.append('<td width="100%" align="center">None</td>')
    text.append('</tr>')

    text.append('<tr><td align="center">Top 16 solved</td></tr>')

    text.append('<tr>')
    solved = info['real_solved']
    solved = sorted(solved, key=lambda x: (x[3], x[4], x[0]))
    total = min(16, len(solved))

    if total > 0:
      text.append('<td valign="top"><table cellpadding="3" width="100%">')
      text.append(
          '<tr><td>Id</td><td>Title</td><td>Accepted</td><td>Submit</td><td>AC Ratio</td><td>Score</td></tr>'
      )
      for i in range(0, total):
        text.append(
            '<tr><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%.2f%%</td><td>%f</td></tr>'
            % (solved[i][0], solved[i][1], solved[i][3], solved[i][2],
               100 * solved[i][4], solved[i][5]))
      text.append('</table></td>')
    else:
      text.append('<td width="100%" align="center">None</td>')
    text.append('</tr>')

    print('\r\n'.join(text))
  elif cmd == 'cmp':
    if len(sys.argv) <= 3:
      print('error!')
      return
    user1, user2 = urllib.parse.unquote(sys.argv[2]), urllib.parse.unquote(
        sys.argv[3])
    info1 = get_user_info(user1)
    if not 'error' in info1 or info1['error'] != 0:
      print('error!')
      return
    info2 = get_user_info(user2)
    if not 'error' in info2 or info2['error'] != 0:
      print('error!')
      return
    both, first, second = merge_solved(sorted(info1['real_solved']),
                                       sorted(info2['real_solved']))

    text = []
    text.append('<table cellpadding="1" width="1080" border="1">')
    text.append(
        '<tr><td></td><td align="center">%s</td><td align="center">%s</td></tr>'
        % (html.escape(user1), html.escape(user2)))
    text.append(
        '<tr><td>Solved</td><td align="center">%d</td><td align="center">%d</td></tr>'
        % (len(info1['real_solved']), len(info2['real_solved'])))
    text.append(
        '<tr><td>Score</td><td align="center">%f</td><td align="center">%f</td></tr>'
        % (info1['total_score'], info2['total_score']))
    progress1 = 100. * len(info1['real_solved']) / (len(info1['real_solved']) +
                                                    len(info1['real_unsolved']))
    progress2 = 100. * len(info2['real_solved']) / (len(info2['real_solved']) +
                                                    len(info2['real_unsolved']))
    text.append(
        '<tr><td>Progress</td><td align="center">%.2f%%</td><td align="center">%.2f%%</td></tr>'
        % (progress1, progress2))
    text.append('<tr><td valign="top" rowspan="2">Problem Difference</td>')
    text.append('<td align="center">%d</td><td align="center">%d</td></tr>' %
                (len(first), len(second)))

    text.append('<tr><td valign="top" align="center" width="42%">')
    temp = []
    for idx, i in enumerate(first):
      temp.append('%s&nbsp;' % i[0])
      if (idx + 1) % 10 == 0:
        temp.append('<br/>')
    text.append(''.join(temp))
    text.append('</td>')

    text.append('<td valign="top" align="center" width="42%">')
    temp = []
    for idx, i in enumerate(second):
      temp.append('%s&nbsp;' % i[0])
      if (idx + 1) % 10 == 0:
        temp.append('<br/>')
    text.append(''.join(temp))
    text.append('</td>')
    text.append('</tr>')

    text.append('</table>')
    print('\r\n'.join(text))
  elif cmd == "soj_info":
    db = soj_db.load_db(problems_db_path)
    text = []
    text.append('<table cellpadding="1" border="0" width="100%">')
    text.append('<tr><td>Total Problems</td><td>%d</td></tr>' % db['count'])
    text.append('<tr><td>Available Problems</td><td>%d</td></tr>' %
                db['enabled'])
    text.append('<tr><td>0 AC</td><td>%d</td></tr>' % db['zero_ac'])
    text.append('</table>')
    print('\r\n'.join(text))
  elif cmd == "sol_table":
    sol = soj_db.load_sol(solutions_db_path)
    av_sol = {
        item['id']: item
        for item in sol['solutions']
        if 'etag' in item and len(item['etag']) > 0
    }
    sdb = soj_db.load_db(problems_db_path)
    all_id = sorted([
        k for (k, v) in sdb['problems'].items()
        if 'enable' in v and v['enable'] > 0
    ],
                    key=lambda x: int(x))
    text = []
    text.append('<table cellpadding="1" border="1">')
    blocks = {}
    for curr in all_id:
      val = int(curr)
      which = val // 100 - 10
      if not which in blocks:
        blocks[which] = []
      if curr in av_sol:
        blocks[which].append((1, curr))
      else:
        blocks[which].append((0, curr))
    for volume in sorted([k for (k, v) in blocks.items()]):
      text.append('<tr><td align="center">volume %d (%d problems)</td></tr>' %
                  (volume, len(blocks[volume])))
      text.append('<tr><td>')
      orz = []
      for item in enumerate(blocks[volume]):
        solved = item[1][0]
        id = item[1][1]
        if solved > 0:
          orz.append('<a href="solution_detail.php?id=%s">%s</a>&nbsp;' %
                     (id, id))
        else:
          orz.append('%s&nbsp;' % id)
        if (item[0] + 1) % 10 == 0:
          orz.append('<br/>')
      text.append(''.join(orz))
      text.append('</td></tr>')
    text.append('</table>')
    print('\r\n'.join(text))
  elif cmd == 'sol_detail':
    if len(sys.argv) <= 2:
      print('error!')
      return
    id = sys.argv[2]
    sol = soj_db.load_sol(solutions_db_path)
    av_sol = {
        item['id']: item
        for item in sol['solutions']
        if 'etag' in item and len(item['etag']) > 0
    }
    if not id in av_sol:
      print('solution does not exist!')
      return
    detail = av_sol[id]
    text = []
    text.append('<table cellpadding="1" border="1" width="600">')
    text.append('<tr><td width="20%%">Id</td><td>%s</td></tr>' % id)
    text.append(
        '<tr><td>Title</td><td><a href="%s/soj/problem.action?id=%s" target="_blank"">%s</a></td></tr>'
        % (soj_db.soj_prefix, id, detail['title']))
    text.append('<tr><td>Tags</td><td>%s</td></tr>' %
                '<br/>'.join(detail['etag'].split(',')))
    text.append('<tr><td>Brief solution</td><td>%s</td></tr>' %
                html.escape(detail['brief_solution']))
    text.append('</table>')
    print('\r\n'.join(text))
  else:
    print('error!')


if __name__ == "__main__":
  work_html()
