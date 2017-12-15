"""
    src/__main__.py

    Main entry point for the CLI.

"""

import argparse, json, requests, sys
from bs4 import BeautifulSoup
from .Course import Course

SCRIPT_DESCRIPTION=""" 
    A command-line interface for scraping course information the University of Colorado Boulder Course Catalog
    by subject. Returns output in JSON to standard output.
    """

def scrape_page(url):
    """
    Scrape a web page with divs of the class "courseblock".

    :param url: valid URL of a CU Course Catalog page to scrape.
    :return: A list of Course instances.
    """
    out = []
    results = requests.get(url)
    soup = BeautifulSoup(results.content, 'html.parser')
    courses = soup.find_all('div', 'courseblock')
    for c in courses:
        course = Course(c)
        out.append(course)
    return out

def main():
    """
    Main entry point for the script.

    :return: Writes JSON to stdout
    """
    parser = argparse.ArgumentParser(SCRIPT_DESCRIPTION)
    parser.add_argument('subject', metavar="SUBJ", nargs='*', type=str,
                        help="A space separated list of subject abbreviation, e.g. CSCI or ENGL. Is case insensitive.")
    args = parser.parse_args()

    url_base = 'https://catalog.colorado.edu/courses-a-z'
    nodes = {}

    for subject in args.subject:
        url = '{}/{}'.format(url_base, subject.lower())
        for course in scrape_page(url):
            course_id = '{} {}'.format(course['subject'], course['number'])
            nodes[course_id] = course

    json.dump(nodes, sys.stdout, indent=2)
    print('')


if __name__ == '__main__':
    main()
