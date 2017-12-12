"""

    cu_course_scraper/main.py

    @author: Stephen Kasica <stephen.kaica@colorado.edu>

"""

import argparse, requests, json, re, sys, os
from bs4 import BeautifulSoup
from bs4.element import NavigableString

class Course(dict):

    def __init__(self, cb):
        """

        :param cb:
        """

        dict.__init__(self)
        title_class = 'courseblocktitle'
        desc_class = 'courseblockdesc'
        extra_class = 'courseblockextra'

        def parse_extra_block(eb):

            extra_category_map = {
                'Equivalent - Duplicate Degree Credit Not Granted: ': 'dupes',
                'Additional Information: ': 'misc',
                'Recommended: ': 'recs',
                'Requisites: ': 'reqs',
                'Grading Basis: ': 'grade',
                'Repeatable: ': 'reps'
            }

            data = {}

            for c in range(0, len(eb.contents)):
                if eb.contents[c].name == 'strong':  # start
                    key = extra_category_map.get(eb.contents[c].text, eb.contents[c].text)
                    data[key] = ''
                elif isinstance(eb.contents[c], NavigableString):
                    data[key] += eb.contents[c].string
                elif eb.contents[c].name in ['a', 'span']:
                    data[key] += eb.contents[c].text
            return data

        def parse_title_block(t):
            ptrn = re.compile('^(\w{4})\s(\d{4})\s+\(([\d-]+)\)\s([^\n]+)$')
            matches = ptrn.findall(t)
            return matches[0]

        title_block = cb.find('p', title_class).string
        title_data = parse_title_block(title_block)
        dict.__setitem__(self, 'subject', title_data[0])
        dict.__setitem__(self, 'number', title_data[1])
        dict.__setitem__(self, 'credits', title_data[2])
        dict.__setitem__(self, 'title', title_data[3])

        desc_block = cb.find('p', desc_class)
        dict.__setitem__(self, 'desc', desc_block.text[1:])  # text starts with newline char

        extra_block = cb.find('p', extra_class)
        if extra_block:
            extras = parse_extra_block(extra_block)
            dict.__setitem__(self, 'dupes', extras.get('dupes', None))
            dict.__setitem__(self, 'misc',extras.get('misc', None))
            dict.__setitem__(self, 'recs', extras.get('recs', None))
            dict.__setitem__(self, 'reqs', extras.get('reqs', None))
            dict.__setitem__(self, 'grade', extras.get('grade', None))
            dict.__setitem__(self, 'reps', extras.get('reps', None))

def getDataFromPage(url):
    out = []
    results = requests.get(url)
    soup = BeautifulSoup(results.content, 'html.parser')
    courses = soup.find_all('div', 'courseblock')
    for c in courses:
        course = Course(c)
        out.append(course)
    return out

def main():
    parser = argparse.ArgumentParser("""
        A CLI for scraping course information from the University of Colorado Boulder
        """)
    parser.add_argument('subject', metavar="SUBJ", nargs='*')
    args = parser.parse_args()

    url_base = 'https://catalog.colorado.edu/courses-a-z'
    nodes = []

    for subject in args.subject:
        url = '{}/{}'.format(url_base, subject)
        for course in getDataFromPage(url):
            nodes.append(course)

    json.dump(nodes, sys.stdout, indent=2)
    print('')

if __name__ == '__main__':
    main()
