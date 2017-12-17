"""
    src/Course.py

    A class for representing HTML-structured data in the courseblock classed divs as a dictionary.
"""

from bs4.element import NavigableString
import re

class Course(dict):

    def __init__(self, cb):
        """
        Override the default dictionary initialization method to construct a dictionary from the HTML of an
        element from the CU Course Catalog with a course block class.

        :param cb: a course block HTML markup (results from bs4's find_all function)
        """

        dict.__init__(self)

        title_block = cb.find('p', 'courseblocktitle').string
        title_data = re.findall('^(\w{4})\s(\d{4})\s+\(([\d-]+)\)\s([^\n]+)$', title_block)[0]
        dict.__setitem__(self, 'subject', title_data[0])
        dict.__setitem__(self, 'number', title_data[1])
        dict.__setitem__(self, 'credits', title_data[2])
        dict.__setitem__(self, 'title', title_data[3])

        desc_block = cb.find('p', 'courseblockdesc')
        desc = str(desc_block.text[1:]).replace('\u00A0', ' ')  # text starts with newline char, slice it off
        dict.__setitem__(self, 'desc', desc)

        extra_block = cb.find('p', 'courseblockextra')
        if extra_block:
            extras = self.__parse_extra_block(extra_block)
            dict.__setitem__(self, 'aliases', extras.get('Equivalent - Duplicate Degree Credit Not Granted: ', None))
            dict.__setitem__(self, 'miscellaneous', extras.get('Additional Information: ', None))
            dict.__setitem__(self, 'recommendations', extras.get('Recommended: ', None))
            dict.__setitem__(self, 'restrictions', extras.get('Requisites: ', None))
            dict.__setitem__(self, 'grading', extras.get('Grading Basis: ', None))
            dict.__setitem__(self, 'repeatable', extras.get('Repeatable: ', 'No'))

        dict.__setitem__(self, 'course_requirements', self.__get_requirements(dict.__getitem__(self, 'restrictions')))

    def __parse_extra_block(self, eb):
        """
        Transform the HTML block of extra course information, grading policy, requesite courses, etc...
        into a dictionary.

        :param eb: extra block HTML content (results from bs4's find function)
        :return: A dictionary of present values where words in bold represent keys and the text that follows are the
        values.
        """

        data = {}

        for c in range(0, len(eb.contents)):
            if eb.contents[c].name == 'strong':  # start
                key = eb.contents[c].text
                data[key] = ''
            elif isinstance(eb.contents[c], NavigableString):
                data[key] += eb.contents[c].string.replace('\u00A0', ' ')
            elif eb.contents[c].name in ['a', 'span']:
                data[key] += str(eb.contents[c].text).replace('\u00A0', ' ')
        return data

    def __get_requirements(self, requirements):
        """
        Parses a string of prerequesite courses from CU's course catalog into a tree structure representing
        the different types of dependencies between courses. This method is essentially a boolean expression parser
        writen by someone who knows nothing of natural language processing. While these strings resemble boolean
        expressions, the actual text doesn't follow the rules. Thus, results may contain slight errors.

        :param requirements: A test string containing course requirements, if any.
        :return: An multi-dimensional array representing relationship between dependencies
        """

        def recurse(reqs):
            """
            A recursive algorithm for representing strings of prerequisite courses as a tree.

            :param reqs: A substring only containing course subject code (4 chars) course number (4 chars) the words
            "and" and/or the word "or", e.g. "CSCI 1989 and CSCI 1776 or MATH 1491 or APPM 2001"
            :return: An multi-dimensional array where AND relationships are a list of lists and OR relationships are
            a list of strings.
            """
            if 'and' in reqs:
                reqs = reqs.split(' and ')
                for i in range(0, len(reqs)):
                    reqs[i] = recurse(reqs[i])
            else:
                # base case
                reqs = reqs.split(' or ')

            return reqs

        if not requirements:
            return []

        match = re.search('([A-z]{4}\s[0-9]{4}(?:\s(?:and|or)\s)?)+', requirements)

        if not match:
            return []

        return recurse(match.group(0))
