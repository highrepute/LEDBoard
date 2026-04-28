import sys
import os
import datetime
import random as random_module

# Ensure repo root (data layer) is importable
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WEB_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _WEB_DIR)

from flask import Flask, session, request, jsonify, send_file, render_template, abort

from const import const
from problemFuncs import problemClass
from usersFuncs import userClass
from logFuncs import logClass
from projectFuncs import projectClass
from boardMaker import boardMaker
import leds

const.initConfigVariables()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'ledboard-dev-secret')
app.permanent_session_lifetime = datetime.timedelta(seconds=const.LOGOUTTIMEOUT)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _current_user():
    return session.get('user')


def _require_login():
    user = _current_user()
    if not user:
        abort(401)
    return user


def _require_admin():
    user = _require_login()
    if user != const.ADMIN:
        abort(403)
    return user


def _serialize_problem(row_idx, prob):
    """Serialize a problem row (full columns) to a dict for the API."""
    grade = int(prob[const.GRADECOL]) if prob[const.GRADECOL] else 0
    stars = int(prob[const.STARSCOL]) if prob[const.STARSCOL] else 0
    tags = [prob[const.TAGSCOL + i] for i in range(10)
            if const.TAGSCOL + i < len(prob) and prob[const.TAGSCOL + i]]
    footholdset = prob[const.FOOTHOLDSETCOL] if len(prob) > const.FOOTHOLDSETCOL else ''
    return {
        'row': row_idx,
        'name': prob[const.PROBNAMECOL],
        'grade': grade,
        'grade_label': const.GRADES[grade] if 0 <= grade < len(const.GRADES) else str(grade),
        'stars': stars,
        'stars_label': const.STARS[stars] if 0 <= stars < len(const.STARS) else '-',
        'date': prob[const.DATECOL],
        'user': prob[const.USERCOL],
        'notes': prob[const.NOTESCOL] if len(prob) > const.NOTESCOL else '',
        'footholdset': footholdset,
        'tags': tags,
    }


def _get_holds(prob):
    """Extract start, problem, and finish hold lists from a full problem row."""
    start_holds = []
    for i in range(const.STARTHOLDSINDEX, const.STARTHOLDSINDEX + 2):
        if i < len(prob) and prob[i] != '':
            val = int(prob[i])
            if val > 0:
                start_holds.append(val)

    fin_holds = []
    for i in range(const.FINHOLDSINDEX, const.FINHOLDSINDEX + 2):
        if i < len(prob) and prob[i] != '':
            val = int(prob[i])
            if val > 0:
                fin_holds.append(val)

    prob_holds = []
    if len(prob) > const.NOHOLDSINDEX and prob[const.NOHOLDSINDEX] != '':
        n_holds = int(prob[const.NOHOLDSINDEX])
        for i in range(const.HOLDSINDEX, const.HOLDSINDEX + n_holds):
            if i < len(prob):
                prob_holds.append(int(prob[i]))

    return start_holds, prob_holds, fin_holds


def _heatmap_color(count, min_count, max_count):
    v = const.LED_VALUE
    if count == 0:
        return (0, v, 0)
    if max_count == min_count:
        return (v, v, 0)  # all used holds equal → yellow
    ratio = (count - min_count) / (max_count - min_count)
    if ratio < 0.5:
        t = ratio / 0.5
        return (int(v * t), v, 0)
    else:
        t = (ratio - 0.5) / 0.5
        return (v, int(v * (1 - t)), 0)


def _compute_heatmap():
    problems_db = problemClass.readProblemFile()
    counts = [0] * (const.TOTAL_LED_COUNT + 1)  # 1-indexed
    for row in problems_db[1:]:
        for col in range(const.STARTHOLDSINDEX, const.FINHOLDSINDEX):
            try:
                h = int(row[col])
                if 1 <= h <= const.TOTAL_LED_COUNT:
                    counts[h] += 1
            except (ValueError, IndexError):
                pass
        for col in range(const.FINHOLDSINDEX, const.NOHOLDSINDEX):
            try:
                h = int(row[col])
                if 1 <= h <= const.TOTAL_LED_COUNT:
                    counts[h] += 1
            except (ValueError, IndexError):
                pass
        for col in range(const.HOLDSINDEX, len(row)):
            try:
                h = int(row[col])
                if 1 <= h <= const.TOTAL_LED_COUNT:
                    counts[h] += 1
            except (ValueError, IndexError):
                pass
    return counts


def _grade_votes_to_labels(grade_votes_raw):
    counts = {g: 0 for g in const.GRADES}
    for gv in grade_votes_raw:
        try:
            idx = int(gv)
            label = const.GRADES[idx] if 0 <= idx < len(const.GRADES) else str(gv)
        except (ValueError, TypeError):
            label = str(gv)
        counts[label] = counts.get(label, 0) + 1
    return counts


def _star_votes_to_labels(star_votes_raw):
    counts = {s: 0 for s in const.STARS}
    for sv in star_votes_raw:
        try:
            idx = int(sv)
            label = const.STARS[idx] if 0 <= idx < len(const.STARS) else str(sv)
        except (ValueError, TypeError):
            label = str(sv)
        counts[label] = counts.get(label, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing credentials'}), 400
    users = userClass.readUsersFile()
    result = userClass.checkPassword(users, data['username'], data['password'])
    if result == 0:
        session.permanent = True
        session['user'] = data['username']
        return jsonify({'ok': True, 'username': data['username']})
    return jsonify({'error': 'Invalid username or password'}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'ok': True})


@app.route('/api/me')
def me():
    user = _current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    return jsonify({'username': user})


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    username = data['username'].strip()
    password = data['password']
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    users = userClass.readUsersFile()
    existing = [row[0] for row in users[1:] if row]
    if username in existing:
        return jsonify({'error': 'Username already exists'}), 409
    date = datetime.date.today().isoformat()
    userClass.addNewUser([username, password, date, name, email])
    return jsonify({'ok': True})


# ---------------------------------------------------------------------------
# Config / metadata
# ---------------------------------------------------------------------------

@app.route('/api/config')
def get_config():
    return jsonify({
        'grades': const.GRADES,
        'stars': const.STARS,
        'tags': const.TAGS,
        'theme_colour': const.THEMECOLOUR,
        'default_msg': const.DEFAULTMSG,
        'admin_user': const.ADMIN,
        'footholdsets': const.FOOTHOLDSETS,
    })


@app.route('/api/users')
def get_users():
    users = userClass.readUsersFile()
    names = [row[0] for row in users[1:] if row]
    return jsonify(names)


# ---------------------------------------------------------------------------
# Problems
# ---------------------------------------------------------------------------

@app.route('/api/problems')
def get_problems():
    grade_min = int(request.args.get('grade_min', 0))
    grade_max = int(request.args.get('grade_max', len(const.GRADES) - 1))
    name_filter = request.args.get('name', '').strip().lower()
    user_filter = request.args.get('user', '').strip()
    tags_raw = request.args.get('tags', '').strip()
    tags = [t.strip() for t in tags_raw.split(',') if t.strip()] if tags_raw else []
    projects_only = request.args.get('projects', '0') == '1'

    project_names = set()
    if projects_only:
        user = _current_user()
        if user:
            project_names = set(projectClass.getUserProjects(user))

    all_problems = problemClass.readProblemFile()
    result = []

    for row_idx, prob in enumerate(all_problems):
        if row_idx == 0:
            continue
        if not prob or not prob[0]:
            continue
        if projects_only and prob[const.PROBNAMECOL] not in project_names:
            continue
        try:
            grade = int(prob[const.GRADECOL])
        except (ValueError, IndexError):
            continue
        if grade < grade_min or grade > grade_max:
            continue
        if user_filter and prob[const.USERCOL] != user_filter:
            continue
        name = prob[const.PROBNAMECOL]
        if name_filter and name_filter not in name.lower():
            continue
        if tags:
            prob_tags = [prob[const.TAGSCOL + i]
                         for i in range(10) if const.TAGSCOL + i < len(prob)]
            if not all(t in prob_tags for t in tags):
                continue
        result.append(_serialize_problem(row_idx, prob))

    return jsonify(result)


@app.route('/api/problems/random')
def get_random_problem():
    grade_min = int(request.args.get('grade_min', 0))
    grade_max = int(request.args.get('grade_max', len(const.GRADES) - 1))
    name_filter = request.args.get('name', '').strip().lower()
    user_filter = request.args.get('user', '').strip()
    tags_raw = request.args.get('tags', '').strip()
    tags = [t.strip() for t in tags_raw.split(',') if t.strip()] if tags_raw else []

    all_problems = problemClass.readProblemFile()
    candidates = []

    for row_idx, prob in enumerate(all_problems):
        if row_idx == 0:
            continue
        if not prob or not prob[0]:
            continue
        try:
            grade = int(prob[const.GRADECOL])
        except (ValueError, IndexError):
            continue
        if grade < grade_min or grade > grade_max:
            continue
        if user_filter and prob[const.USERCOL] != user_filter:
            continue
        name = prob[const.PROBNAMECOL]
        if name_filter and name_filter not in name.lower():
            continue
        if tags:
            prob_tags = [prob[const.TAGSCOL + i]
                         for i in range(10) if const.TAGSCOL + i < len(prob)]
            if not all(t in prob_tags for t in tags):
                continue
        candidates.append((row_idx, prob))

    if not candidates:
        return jsonify({'error': 'No matching problems'}), 404

    row_idx, prob = random_module.choice(candidates)
    return jsonify(_serialize_problem(row_idx, prob))


@app.route('/api/problems/<int:row>/votes')
def get_problem_votes(row):
    try:
        prob = problemClass.getProblem(row)
    except (IndexError, TypeError):
        return jsonify({'error': 'Problem not found'}), 404

    prob_name = prob[const.PROBNAMECOL]
    return jsonify({
        'star_votes': _star_votes_to_labels(logClass.getStarVotes(prob_name)),
        'grade_votes': _grade_votes_to_labels(logClass.getGradeVotes(prob_name)),
    })


@app.route('/api/problems/<int:row>')
def get_problem(row):
    try:
        prob = problemClass.getProblem(row)
    except (IndexError, TypeError):
        return jsonify({'error': 'Problem not found'}), 404

    data = _serialize_problem(row, prob)
    start_holds, prob_holds, fin_holds = _get_holds(prob)
    data['startHolds'] = start_holds
    data['probHolds'] = prob_holds
    data['finHolds'] = fin_holds

    ascents = logClass.getProblemAscents(prob[const.PROBNAMECOL])
    data['ascent_count'] = max(0, len(ascents) - 1)

    user = _current_user()
    if user:
        data['is_project'] = projectClass.isProject(user, prob[const.PROBNAMECOL])

    return jsonify(data)


# ---------------------------------------------------------------------------
# Board image and hold overlay
# ---------------------------------------------------------------------------

@app.route('/board-image')
def board_image():
    image_path = boardMaker.getBoardImagePath(const.BOARDNAME)
    if not os.path.exists(image_path):
        abort(404)
    return send_file(image_path)


@app.route('/api/board')
def get_board():
    holds_raw = boardMaker.loadBoard(const.BOARDNAME)

    half = const.HOLDBUTTONSIZE / 2.0
    fw, fh = const.BOARDFRAMEWIDTH, const.BOARDFRAMEHEIGHT

    holds = []
    for row in holds_raw:
        if len(row) < 3:
            continue
        try:
            hold_id = int(row[0])
            x = int(row[1])
            y = int(row[2])
            label = row[3] if len(row) > 3 else str(hold_id)
        except (ValueError, IndexError):
            continue

        holds.append({
            'id': hold_id,
            'label': label,
            'x_pct': round((x + half) / fw * 100, 3),
            'y_pct': round((y + half) / fh * 100, 3),
        })

    mirror_table = []
    try:
        mirror_table = boardMaker.getBoardMirrorTable(const.BOARDNAME)
    except Exception:
        pass

    return jsonify({
        'holds': holds,
        'image_url': '/board-image',
        'mirror_table': mirror_table,
    })


# ---------------------------------------------------------------------------
# LED control
# ---------------------------------------------------------------------------

@app.route('/api/light/<int:row>', methods=['POST'])
def light_problem(row):
    try:
        prob = problemClass.getProblem(row)
    except (IndexError, TypeError):
        return jsonify({'error': 'Problem not found'}), 404

    start_holds, prob_holds, fin_holds = _get_holds(prob)
    leds.light_problem(start_holds, prob_holds, fin_holds)
    return jsonify({'ok': True})


@app.route('/api/light/off', methods=['POST'])
def light_off():
    leds.off()
    return jsonify({'ok': True})


@app.route('/api/light/heatmap', methods=['POST'])
def light_heatmap():
    counts = _compute_heatmap()
    used = [c for c in counts[1:] if c > 0]
    min_count = min(used) if used else 0
    max_count = max(used) if used else 0
    pixels = [[i, *_heatmap_color(counts[i + 1], min_count, max_count)]
              for i in range(const.TOTAL_LED_COUNT)]
    leds.raw(pixels)
    return jsonify({'ok': True})


@app.route('/api/light/custom', methods=['POST'])
def light_custom():
    data = request.get_json() or {}
    start = data.get('start', [])
    prob = data.get('prob', [])
    fin = data.get('fin', [])
    leds.light_problem(start, prob, fin)
    return jsonify({'ok': True})


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

@app.route('/api/log', methods=['POST'])
def log_climb():
    user = _require_login()
    data = request.get_json()
    if not data or 'problem_name' not in data:
        return jsonify({'error': 'Missing problem_name'}), 400

    grade_label = data.get('grade', '')
    stars_label = data.get('stars', '-')
    style = data.get('style', '')
    comments = data.get('comments', '')
    date = datetime.date.today().isoformat()

    grade_index = const.GRADES.index(grade_label) if grade_label in const.GRADES else grade_label
    stars_index = const.STARS.index(stars_label) if stars_label in const.STARS else stars_label

    new_log = [user, data['problem_name'], grade_index, stars_index, date, comments, style]
    logClass.logProblem(new_log)
    return jsonify({'ok': True})


@app.route('/api/logbook')
def get_logbook():
    user = _require_login()
    logbook = logClass.getUserLogbook(user)
    entries = []
    for row in logbook[1:]:  # skip header at index 0
        grade_raw = row[1] if len(row) > 1 else ''
        try:
            g_idx = int(grade_raw)
            grade = const.GRADES[g_idx] if 0 <= g_idx < len(const.GRADES) else str(grade_raw)
        except (ValueError, TypeError):
            grade = str(grade_raw)

        stars_raw = row[2] if len(row) > 2 else ''
        try:
            s_idx = int(stars_raw)
            stars = const.STARS[s_idx] if 0 <= s_idx < len(const.STARS) else str(stars_raw)
        except (ValueError, TypeError):
            stars = str(stars_raw)

        entries.append({
            'problem': row[0] if len(row) > 0 else '',
            'grade': grade,
            'stars': stars,
            'date': row[3] if len(row) > 3 else '',
            'comments': row[4] if len(row) > 4 else '',
            'style': row[5] if len(row) > 5 else '',
        })
    return jsonify(entries)


@app.route('/api/logbook/names')
def get_logbook_names():
    user = _current_user()
    if not user:
        return jsonify([])
    names = logClass.getUserLoggedProblemNames(user)
    return jsonify(list(names))


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

@app.route('/api/projects', methods=['GET'])
def get_projects():
    user = _require_login()
    return jsonify(projectClass.getUserProjects(user))


@app.route('/api/projects/<path:problem_name>', methods=['POST'])
def toggle_project(problem_name):
    user = _require_login()
    if projectClass.isProject(user, problem_name):
        projectClass.removeProject(user, problem_name)
        return jsonify({'is_project': False})
    else:
        projectClass.addProject(user, problem_name)
        return jsonify({'is_project': True})


# ---------------------------------------------------------------------------
# Admin endpoints
# ---------------------------------------------------------------------------

@app.route('/api/admin/users')
def admin_get_users():
    _require_admin()
    users = userClass.readUsersFile()
    result = []
    for row in users[1:]:
        if not row:
            continue
        result.append({
            'username': row[0] if len(row) > 0 else '',
            'date': row[2] if len(row) > 2 else '',
            'name': row[3] if len(row) > 3 else '',
            'email': row[4] if len(row) > 4 else '',
        })
    return jsonify(result)


@app.route('/api/admin/users/<username>', methods=['DELETE'])
def admin_delete_user(username):
    _require_admin()
    users = userClass.readUsersFile()
    new_users = [users[0]] + [r for r in users[1:] if r and r[0] != username]
    userClass.saveUsersFile(new_users)
    return jsonify({'ok': True})


@app.route('/api/admin/logs')
def admin_get_logs():
    _require_admin()
    log = logClass.readLogFile()
    result = []
    for idx, row in enumerate(log):
        if idx == 0 or not row:
            continue
        grade_raw = row[2] if len(row) > 2 else ''
        try:
            g_idx = int(grade_raw)
            grade = const.GRADES[g_idx] if 0 <= g_idx < len(const.GRADES) else str(grade_raw)
        except (ValueError, TypeError):
            grade = str(grade_raw)
        stars_raw = row[3] if len(row) > 3 else ''
        try:
            s_idx = int(stars_raw)
            stars = const.STARS[s_idx] if 0 <= s_idx < len(const.STARS) else str(stars_raw)
        except (ValueError, TypeError):
            stars = str(stars_raw)
        result.append({
            'idx': idx,
            'username': row[0] if len(row) > 0 else '',
            'problem': row[1] if len(row) > 1 else '',
            'grade': grade,
            'stars': stars,
            'date': row[4] if len(row) > 4 else '',
            'comments': row[5] if len(row) > 5 else '',
            'style': row[6] if len(row) > 6 else '',
        })
    return jsonify(result)


@app.route('/api/admin/logs/<int:idx>', methods=['DELETE'])
def admin_delete_log(idx):
    _require_admin()
    log = logClass.readLogFile()
    if idx <= 0 or idx >= len(log):
        return jsonify({'error': 'Invalid log index'}), 404
    del log[idx]
    logClass.saveLogFile(log)
    return jsonify({'ok': True})


@app.route('/api/admin/problems/<int:row>', methods=['PATCH'])
def admin_edit_problem(row):
    _require_admin()
    data = request.get_json() or {}
    try:
        prob = problemClass.getProblem(row)
    except (IndexError, TypeError):
        return jsonify({'error': 'Problem not found'}), 404

    if 'name' in data:
        prob[const.PROBNAMECOL] = data['name']
    if 'grade' in data:
        gl = data['grade']
        prob[const.GRADECOL] = str(const.GRADES.index(gl)) if gl in const.GRADES else str(gl)
    if 'stars' in data:
        sl = data['stars']
        prob[const.STARSCOL] = str(const.STARS.index(sl)) if sl in const.STARS else str(sl)
    if 'footholdset' in data:
        prob[const.FOOTHOLDSETCOL] = data['footholdset']
    if 'notes' in data:
        prob[const.NOTESCOL] = data['notes']

    problemClass.updateProblemFile(prob, row)
    return jsonify({'ok': True})


@app.route('/api/admin/config')
def admin_get_config():
    _require_admin()
    return jsonify({
        'LINUX': const.LINUX,
        'LEDBRIGHTNESS': const.LED_VALUE,
        'DEFAULTMSG': const.DEFAULTMSG,
        'GRADES': const.GRADES,
        'STARS': const.STARS,
        'TAGS': const.TAGS,
        'FOOTHOLDSETS': const.FOOTHOLDSETS,
        'TOTALLEDCOUNT': const.TOTAL_LED_COUNT,
        'ADMIN': const.ADMIN,
        'THEMECOLOUR': const.THEMECOLOUR,
        'LOGOUTTIMEOUT': const.LOGOUTTIMEOUT,
        'USERSPATH': const.USERSPATH,
        'LOGPATH': const.LOGPATH,
        'PROBPATH': const.PROBPATH,
        'PROJECTSPATH': const.PROJECTSPATH,
        'BOARDNAME': const.BOARDNAME,
        'IMAGEPATH': const.IMAGEPATH,
    })


@app.route('/api/admin/config', methods=['POST'])
def admin_save_config():
    _require_admin()
    data = request.get_json() or {}

    if 'LINUX' in data:
        const.setLINUX(int(data['LINUX']))
    if 'LEDBRIGHTNESS' in data:
        const.setLED_VALUE(int(data['LEDBRIGHTNESS']))
    if 'DEFAULTMSG' in data:
        const.setDEFAULTMSG(str(data['DEFAULTMSG']))
    if 'GRADES' in data:
        v = data['GRADES']
        const.setGRADES(str(v) if isinstance(v, list) else v)
    if 'STARS' in data:
        v = data['STARS']
        const.setSTARS(str(v) if isinstance(v, list) else v)
    if 'TAGS' in data:
        v = data['TAGS']
        const.setTAGS(str(v) if isinstance(v, list) else v)
    if 'FOOTHOLDSETS' in data:
        v = data['FOOTHOLDSETS']
        const.setFOOTHOLDSETS(str(v) if isinstance(v, list) else v)
    if 'TOTALLEDCOUNT' in data:
        const.setTOTAL_LED_COUNT(int(data['TOTALLEDCOUNT']))
    if 'ADMIN' in data:
        const.setADMIN(str(data['ADMIN']))
    if 'THEMECOLOUR' in data:
        const.setTHEMECOLOUR(str(data['THEMECOLOUR']))
    if 'LOGOUTTIMEOUT' in data:
        const.setLOGOUTTIMEOUT(int(data['LOGOUTTIMEOUT']))
    if 'USERSPATH' in data:
        const.setUSERSPATH(str(data['USERSPATH']))
    if 'LOGPATH' in data:
        const.setLOGPATH(str(data['LOGPATH']))
    if 'PROBPATH' in data:
        const.setPROBPATH(str(data['PROBPATH']))
    if 'PROJECTSPATH' in data:
        const.setPROJECTSPATH(str(data['PROJECTSPATH']))

    return jsonify({'ok': True})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
