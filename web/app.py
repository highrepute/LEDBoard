import sys
import os
import datetime

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


def _serialize_problem(row_idx, prob):
    """Serialize a problem row (full columns) to a dict for the API."""
    grade = int(prob[const.GRADECOL]) if prob[const.GRADECOL] else 0
    stars = int(prob[const.STARSCOL]) if prob[const.STARSCOL] else 0
    tags = [prob[const.TAGSCOL + i] for i in range(10)
            if const.TAGSCOL + i < len(prob) and prob[const.TAGSCOL + i]]
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
    })


@app.route('/api/users')
def get_users():
    users = userClass.readUsersFile()
    names = [row[0] for row in users[1:] if row]  # skip header
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

    all_problems = problemClass.readProblemFile()
    result = []

    for row_idx, prob in enumerate(all_problems):
        if row_idx == 0:
            continue  # skip header
        if not prob or not prob[0]:
            continue

        # Grade filter
        try:
            grade = int(prob[const.GRADECOL])
        except (ValueError, IndexError):
            continue
        if grade < grade_min or grade > grade_max:
            continue

        # User filter
        if user_filter and prob[const.USERCOL] != user_filter:
            continue

        # Name filter
        name = prob[const.PROBNAMECOL]
        if name_filter and name_filter not in name.lower():
            continue

        # Tags filter (all requested tags must be present)
        if tags:
            prob_tags = [prob[const.TAGSCOL + i]
                         for i in range(10) if const.TAGSCOL + i < len(prob)]
            if not all(t in prob_tags for t in tags):
                continue

        result.append(_serialize_problem(row_idx, prob))

    return jsonify(result)


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

    # Ascent count
    ascents = logClass.getProblemAscents(prob[const.PROBNAMECOL])
    data['ascent_count'] = max(0, len(ascents) - 1)  # subtract header row

    # Project status for current user
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
    image_path = boardMaker.getBoardImagePath(const.BOARDNAME)

    # Get image dimensions for percentage conversion
    img_width, img_height = None, None
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            img_width, img_height = img.size
    except Exception:
        pass

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

        entry = {'id': hold_id, 'label': label}
        if img_width and img_height:
            entry['x_pct'] = round(x / img_width * 100, 3)
            entry['y_pct'] = round(y / img_height * 100, 3)
        else:
            # Fallback: raw pixels (JS will need image dimensions separately)
            entry['x_px'] = x
            entry['y_px'] = y
        holds.append(entry)

    return jsonify({
        'holds': holds,
        'image_url': '/board-image',
        'img_width': img_width,
        'img_height': img_height,
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
    # getUserLogbook returns reversed list with header at index 0 - skip it
    entries = []
    for row in logbook[1:]:
        entries.append({
            'problem': row[0] if len(row) > 0 else '',
            'grade': row[1] if len(row) > 1 else '',
            'stars': row[2] if len(row) > 2 else '',
            'date': row[3] if len(row) > 3 else '',
            'comments': row[4] if len(row) > 4 else '',
            'style': row[5] if len(row) > 5 else '',
        })
    return jsonify(entries)


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
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
