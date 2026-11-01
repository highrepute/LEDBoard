# -*- coding: utf-8 -*-
"""
Startup checks for the CSV data files (users, logs, problems, projects).

Each file is checked once at startup so the rest of the app can trust it:
  - missing file           -> created with its default header
  - unrecognised / empty   -> original backed up, replaced with a fresh file
  - blank lines            -> dropped
  - short rows (fixable)   -> padded with empty cells
  - rows that can't be trusted -> moved to <name>_rejected_<timestamp>.csv

The original file is always backed up before it is rewritten.
Kept Python 3.5 compatible (no f-strings) for the Pi 3.
"""

import csv
import datetime
import os
import shutil

from const import const

# csv dialect arguments each file is read and written with
EXCEL = {'dialect': 'excel'}
PIPE = {'delimiter': ',', 'quotechar': '|'}


def _isInt(value):
    try:
        int(value)
        return True
    except (TypeError, ValueError):
        return False


def _isIndexOrLabel(value, labels):
    """Valid if it's a label from the list or an int index into it."""
    if value in labels:
        return True
    return _isInt(value) and 0 <= int(value) < len(labels)


def _isIntOrBlank(value):
    return value == '' or _isInt(value)


# ---------------------------------------------------------------- row checks
# Each returns (row, None) if OK (possibly padded), or (None, reason) to reject.

def _checkUser(row):
    if len(row) < 2 or row[0] == '':
        return None, 'needs at least a username and password'
    return row + [''] * (5 - len(row)), None


def _checkLog(row):
    if len(row) < 4:
        return None, 'needs at least username, problem, grade and stars'
    if row[0] == '' or row[1] == '':
        return None, 'missing username or problem name'
    if not _isIndexOrLabel(row[2], const.GRADES):
        return None, 'grade "{}" is not one of the configured GRADES'.format(row[2])
    if not _isIndexOrLabel(row[3], const.STARS):
        return None, 'stars "{}" is not one of the configured STARS'.format(row[3])
    return row + [''] * (7 - len(row)), None


def _checkProblem(row):
    if len(row) <= const.NOHOLDSINDEX:
        return None, 'too few columns ({}) to hold a problem'.format(len(row))
    if row[const.PROBNAMECOL] == '':
        return None, 'missing problem name'
    grade = row[const.GRADECOL]
    if not (_isInt(grade) and 0 <= int(grade) < len(const.GRADES)):
        return None, 'grade index "{}" not in configured GRADES ({} grades)'.format(
            grade, len(const.GRADES))
    stars = row[const.STARSCOL]
    if not (_isInt(stars) and 0 <= int(stars) < len(const.STARS)):
        return None, 'stars index "{}" not in configured STARS'.format(stars)
    for col in range(const.STARTHOLDSINDEX, const.NOHOLDSINDEX):
        if not _isIntOrBlank(row[col]):
            return None, 'start/finish hold "{}" is not a number'.format(row[col])
    noHolds = row[const.NOHOLDSINDEX]
    if not (_isInt(noHolds) and int(noHolds) > 0):
        return None, 'hold count "{}" is not a positive number'.format(noHolds)
    holds = row[const.HOLDSINDEX:const.HOLDSINDEX + int(noHolds)]
    if len(holds) < int(noHolds):
        return None, 'says {} holds but only {} listed'.format(noHolds, len(holds))
    for hold in holds:
        if not _isInt(hold):
            return None, 'hold "{}" is not a number'.format(hold)
    return row, None


def _checkProject(row):
    if len(row) < 2 or row[0] == '' or row[1] == '':
        return None, 'needs a username and problem name'
    return row, None


# ------------------------------------------------------------ file handling

def _timestamp():
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')


def _sidePath(path, tag):
    root, ext = os.path.splitext(path)
    return '{}_{}_{}{}'.format(root, tag, _timestamp(), ext or '.csv')


def _readRows(path, fmt):
    with open(path, newline='') as f:
        return list(csv.reader(f, **fmt))


def _writeRows(path, rows, fmt):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f, **fmt)
        for row in rows:
            writer.writerow(row)


def _writeFresh(path, kind):
    with open(path, 'w', newline='') as f:
        f.write(const.defaultCsvText(kind))


def _checkFile(name, kind, path, fmt, minHeaderCols, checkRow):
    """Check one data file. Returns a list of human-readable messages."""
    folder = os.path.dirname(path)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)

    if not os.path.exists(path):
        _writeFresh(path, kind)
        return ['{}: not found, created a new one'.format(name)]

    try:
        rows = _readRows(path, fmt)
    except (UnicodeDecodeError, csv.Error) as e:
        rows = None
        reason = 'could not be read ({})'.format(e)

    if rows is not None:
        rows = [r for r in rows if any(cell.strip() for cell in r)]
        if not rows:
            reason = 'was empty'
        elif len(rows[0]) < minHeaderCols:
            reason = 'header has {} columns, expected at least {}'.format(
                len(rows[0]), minHeaderCols)
        else:
            reason = None

    if reason:
        # Not a file we recognise: keep it safe, start fresh
        backup = _sidePath(path, 'unrecognised')
        shutil.copy2(path, backup)
        _writeFresh(path, kind)
        return ['{}: {} - moved to {} and started a new file'.format(
            name, reason, os.path.basename(backup))]

    header, data = rows[0], rows[1:]
    kept, rejected = [], []
    padded = 0
    for row in data:
        fixed, why = checkRow(row)
        if fixed is None:
            rejected.append(row + ['REJECTED: ' + why])
        else:
            if len(fixed) != len(row):
                padded += 1
            kept.append(fixed)

    with open(path, newline='') as f:
        original = f.read()
    blankLines = sum(1 for line in original.splitlines() if not line.strip())

    if not (rejected or padded or blankLines):
        return []

    shutil.copy2(path, _sidePath(path, 'backup'))
    _writeRows(path, [header] + kept, fmt)

    msgs = []
    if blankLines:
        msgs.append('{} blank lines removed'.format(blankLines))
    if padded:
        msgs.append('{} short rows padded'.format(padded))
    if rejected:
        rejectPath = _sidePath(path, 'rejected')
        _writeRows(rejectPath, [header + ['Reason']] + rejected, fmt)
        msgs.append('{} bad rows moved to {}'.format(
            len(rejected), os.path.basename(rejectPath)))
        for row in rejected:
            print('  {} rejected: {}'.format(name, row))
        if data and len(rejected) * 2 > len(data):
            msgs.append('over half the rows rejected - check GRADES/STARS/paths in config.ini')
    return ['{}: {}'.format(name, ', '.join(msgs))]


def checkDataFiles():
    """Check all data files. Returns a list of messages (empty if all fine).
    Never raises: a failure checking one file is reported, not fatal."""
    # old-format problems files (no tag columns) are migrated by readProblemFile
    from problemFuncs import problemClass

    checks = [
        ('users.csv', 'USERS', const.USERSPATH, EXCEL, 2, _checkUser),
        ('logs.csv', 'LOGS', const.LOGPATH, EXCEL, 4, _checkLog),
        ('problems.csv', 'PROBLEMS', const.PROBPATH, EXCEL, 12, _checkProblem),
        ('projects.csv', 'PROJECTS', const.PROJECTSPATH, PIPE, 2, _checkProject),
    ]
    messages = []
    for name, kind, path, fmt, minCols, checkRow in checks:
        try:
            if kind == 'PROBLEMS' and os.path.exists(path):
                rows = _readRows(path, fmt)
                header = rows[0] if rows else []
                if 12 <= len(header) < 17:
                    problemClass.readProblemFile()  # migrates + backs up
                    messages.append('problems.csv: migrated to tag format')
            messages.extend(_checkFile(name, kind, path, fmt, minCols, checkRow))
        except Exception as e:
            messages.append('{}: check failed ({})'.format(name, e))

    for m in messages:
        print('Data check - ' + m)
    return messages
