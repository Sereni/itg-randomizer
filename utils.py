import os
import re
import csv

os.environ['DJANGO_SETTINGS_MODULE'] = 'itg.settings'  # apps aren't loaded yet

import django  # app_label error
from django.conf import settings
if not settings.configured:
    settings.configure()
django.setup()

from itg_assistant.models import Track, Stepchart

# from django.apps import AppConfig

TITLE = re.compile(r'#TITLE:(.+?);')
AUTHOR = re.compile(r'#ARTIST:(.+?);')
BPM = re.compile(r'#BPMS:(.+?);')  # fixme doesn't work with multiline
CHART = re.compile(r'#NOTES:(.+?);')
STOPS = re.compile(r'#STOPS:(.+?)')


def get_bpms(s):
    """
    Parse the BPM string and determine min and max BPM
    :param s: string containing BPM information from simfile
    """
    bpms = sorted([round(float(point.split('=')[-1])) for point in s.split(',')])
    return bpms[0], bpms[-1]


def get_info(s):
    """
    Parse chart string and extract data
    :param s: string containing chart information
    """
    data = s.split([':'])
    style = data[0].split('-')[-1]
    difficulty = data[2]
    num = int(data[3])
    return style, difficulty, num


def process_track(path, pack):
    """
    Create track and stepchart info from .sm file
    :param path: path to .sm file
    :param pack: name of pack
    """
    with open(path) as sm:
        simfile = sm.read()

        # get track info
        title = re.search(TITLE, simfile).group(1)
        author = re.search(AUTHOR, simfile).group(1)
        bpm_string = re.search(BPM, simfile).group(1)
        min_bpm, max_bpm = get_bpms(bpm_string)

        # save track
        track, created = Track.objects.get_or_create(
            name=title,
            author=author,
            pack=pack,
            min_bpm=min_bpm,
            max_bpm=max_bpm
        )

        charts = re.findall(CHART, simfile)
        for chart in charts:
            style, diff_text, diff_num = get_info(chart)
            chart_obj, created = Stepchart.objects.get_or_create(
                track=track,
                diff_num=diff_num,
                diff_text=diff_text,
                style=style
            )


def import_pack(path):
    """
    Import all songs located in a given pack
    :param path: path to song pack
    """
    pack = os.path.basename(path)
    tracks = os.listdir(path)
    for track in tracks:

        # if this is a track directory, process track
        track_dir = os.path.join(path, track)
        if os.path.isdir(track_dir):
            files = os.listdir(track_dir)
            for f in files:
                if f.lower().endswith('.sm'):  # todo add support for .ssc?

                    # this will open .sm and pull stepchart info
                    # track is also created there
                    process_track(os.path.join(track_dir, f), pack=pack)


def get_bpms_unrounded(s):
    bpms = sorted([float(point.split('=')[-1]) for point in s.split(',')])
    return bpms[0], bpms[-1]

def get_sync_info(path):
    """
    Given a path to .sm file, read it and get:
    bpm change or float bpm | stops | name | author | difficulty
    """
    bpm_change = False  # assume constant bpm
    float_bpm = False

    with open(path) as sm:
        simfile = sm.read().replace('\n', ' ')  # this is an ugly hack, don't use it in database

        # get track info
        title = re.search(TITLE, simfile).group(1)
        author = re.search(AUTHOR, simfile).group(1)
        bpm_string = re.search(BPM, simfile).group(1)
        stops = re.search(STOPS, simfile).group(1)
        min_bpm, max_bpm = get_bpms_unrounded(bpm_string)

        if min_bpm != max_bpm:
            bpm_change = True

        if round(max_bpm) != max_bpm:
            float_bpm = True

        first_cell = ''
        if bpm_change:
            first_cell += 'ch '
        if float_bpm:
            first_cell += 'fl'
        if stops != ';':
            stops = 'st'
        else:
            stops = ''

#        chart = re.findall(CHART, simfile)[-1]  # for files with multiple difficulties, most likely last one
 #       style, diff_text, diff_num = get_info(chart)

    return (first_cell, stops, title, author, '')


def process_pack_sync(path):
    """
    Processes pack for sync purposes.
    Analyze all simfiles in the pack and output to csv:
    bpm change or float bpm | stops | name | author | difficulty
    """
    out = open('sync_info.csv', 'w')
    w = csv.writer(out, delimiter=';')

    tracks = os.listdir(path)
    for track in tracks:
        track_dir = os.path.join(path, track)
        if os.path.isdir(track_dir):
            files = os.listdir(track_dir)
            for f in files:
                if f.endswith('.sm'):
                    row = get_sync_info(os.path.join(track_dir, f))
                    w.writerow(row)
                    print('Processed file: %s' % row[2])

# process pack sync is a different kind of parser I needed for syncing the tracklist.
# in the same file, yes.
# process_pack_sync('/Users/Sereni/Downloads/ITG Moscow Tournament 3')


import_pack('/Applications/StepMania/Songs/Ideal Sync')