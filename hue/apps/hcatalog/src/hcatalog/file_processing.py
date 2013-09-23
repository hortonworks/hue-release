# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from hadoop.fs import hadoopfs
import gzip
import xlrd
import logging
import re
import string
from datetime import datetime, date, time


LOG = logging.getLogger(__name__)


class IInterval():

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __repr__(self):
        return '(%d, %d)' % (self.start, self.end)

    def __getitem__(self, key):
        if 0 == key:
            return self.start
        elif 1 == key:
            return self.end
        else:
            return None

class FInterval():

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __repr__(self):
        return '(%f, %f)' % (self.start, self.end)

    def __getitem__(self, key):
        if 0 == key:
            return self.start
        elif 1 == key:
            return self.end
        else:
            return None


def intervals_union(intervals):

    if not intervals:
        return None
    elif len(intervals) == 1:
        return intervals

    intervals.sort(key=lambda self: self.start)
    y = [intervals[0]]
    for x in intervals[1:]:
        if y[-1].end < x.start:
            y.append(x)
        elif y[-1].end == x.start:
            y[-1].end = x.end
    return y


def intervals_intersection(intervals):

    if not intervals:
        return None
    elif len(intervals) == 1:
        return intervals

    intervals.sort(key=lambda self: self.start)
    y = intervals[0]
    for x in intervals[1:]:
        if y.end < x.start:
            return []
        elif y.end == x.start:
            y.start = y.end
        elif y.start <= x.start <= y.end <= x.end:
            y.start = x.start
        elif y.start <= x.start and y.end >= x.end:
            y.start = x.start
            y.end = x.end
        elif x.start <= y.start and y.end <= x.end:
            continue
        elif x.start <= y.start <= x.end <= y.end:
            y.end = x.end
        elif y.start > x.end:
            return []
        elif y.start == x.end:
            y.end = y.start

    return [y]


def intervals_subtraction(intervals, subtrahend):

    if not intervals:
        return None

    intervals.sort(key=lambda self: self.start)
    y = []
    for x in intervals:
        if subtrahend.end < x.start:
            y.append(x)
        elif subtrahend.start < x.start < subtrahend.end < x.end:
            y.append(IInterval(subtrahend.end, x.end))
        elif subtrahend.start < x.start and subtrahend.end > x.end:
            continue
        elif x.start < subtrahend.start and subtrahend.end < x.end:
            y.append(IInterval(x.start, subtrahend.start))
            y.append(IInterval(subtrahend.end, x.end))
        elif x.start < subtrahend.start < x.end < subtrahend.end:
            y.append(IInterval(x.start, subtrahend.start))
        elif subtrahend.start > x.end:
            y.append(x)

    return y


class ExceptionFSM(Exception):
    """
    FSM Exception class.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TransitionTableFSM:
    """Finite State Machine (FSM)."""

    def __init__(self, initial_state, memory=None):

        # Map (input_symbol, current_state) --> (action, next_state).
        self.state_transitions = {}
        # Map (current_state) --> (action, next_state).
        self.state_transitions_any = {}
        self.default_transition = None

        self.input_symbol = None
        self.initial_state = initial_state
        self.current_state = self.initial_state
        self.next_state = None
        self.action = None
        self.memory = memory
        self.initial_memory = memory

    def reset(self):
        self.current_state = self.initial_state
        self.input_symbol = None
        self.memory = self.initial_memory

    def add_transition(self, input_symbol, state, action=None, next_state=None):
        """
        Adds a transition that associates:
            (input_symbol, current_state) --> (action, next_state)
        """

        if next_state is None:
            next_state = state
        self.state_transitions[(input_symbol, state)] = (action, next_state)

    def add_transition_list(self, list_input_symbols, state, action=None, next_state=None):
        """
        Adds the same transition for a list of input symbols.
        """

        if next_state is None:
            next_state = state
        for input_symbol in list_input_symbols:
            self.add_transition(input_symbol, state, action, next_state)

    def add_transition_any(self, state, action=None, next_state=None):
        """
        Adds a transition that associates:
            (current_state) --> (action, next_state)
        """

        if next_state is None:
            next_state = state
        self.state_transitions_any[state] = (action, next_state)

    def set_default_transition(self, action, next_state):
        """
        Sets the default transition.
        """

        self.default_transition = (action, next_state)

    def get_transition(self, input_symbol, state):
        """
        Returns (action, next state) given an input_symbol and state.
        """

        if (input_symbol, state) in self.state_transitions:
            return self.state_transitions[(input_symbol, state)]
        elif state in self.state_transitions_any:
            return self.state_transitions_any[state]
        elif self.default_transition is not None:
            return self.default_transition
        else:
            raise ExceptionFSM('Transition is undefined: (%s, %s).' % (unicode(input_symbol), unicode(state)))

    def process(self, input_symbol):
        """
        The main method to call to process input
        """

        self.input_symbol = input_symbol
        (self.action, self.next_state) = self.get_transition(self.input_symbol, self.current_state)
        if self.next_state is None:
            self.next_state = self.current_state
        if self.action is not None:
            self.action(self)
        self.current_state = self.next_state
        self.next_state = None

    def process_list(self, input_symbols):
        """Takes a list and sends each element to process(). The list may
        be a string or any iterable object. """

        for s in input_symbols:
            self.process(s)


STATE_NONE = 'NONE'
STATE_SLASH = 'SLASH'
STATE_LINE_COMMENT = 'LINE_COMMENT'
STATE_BLOCK_COMMENT = 'BLOCK_COMMENT'
STATE_STAR = 'STAR'


class CommentsDetector():
    """This class provides functionality to detect:
        - java-style comments ('//' - for single line, '/**/' - for block comments)
        - custom single line comments (e.g. '##')
    """

    def __init__(self, java_line_comment=True, java_block_comment=True, custom_line_comment=None):

        self.custom_line_comments = []
        memory = {
            'cur_symbol_pos': None,             # symbolPos
            'cur_line_comment': [None, None],   # [startPos, endPos]
            'cur_block_comment': [None, None],  # [startPos, endPos]
            'line_comments': [],                # [[startPos1, endPos1], [startPos2, endPos2]]
            'block_comments': []                # [[startPos1, endPos1], [startPos2, endPos2]]
        }
        self.java_fsm = TransitionTableFSM(STATE_NONE, memory)
        self.java_line_comment = java_line_comment
        self.java_block_comment = java_block_comment
        self.custom_line_comment = custom_line_comment
        self.custom_comment_end_in_next = False
        if self.custom_line_comment == '//':
            self.java_line_comment = True
            self.custom_line_comment = None

        def do_default(fsm):
            pass
            # print 'Processing default state, state=%s, symbol=\'%s\'' % (fsm.current_state, unicode(fsm.input_symbol))

        def do_other(fsm):
            # print 'do_other current_state=%s, symbol=\'%s\'' % (fsm.current_state, unicode(fsm.input_symbol))
            if fsm.current_state == STATE_SLASH:
                fsm.memory['cur_line_comment'] = [None, None]
                fsm.memory['cur_block_comment'] = [None, None]

        def do_slash_line_only(fsm):
            # print 'do_slash current_state=%s, symbol=\'%s\'' % (fsm.current_state, unicode(fsm.input_symbol))
            if fsm.current_state == STATE_NONE:
                fsm.memory['cur_line_comment'][0] = fsm.memory['cur_symbol_pos']
            elif fsm.current_state == STATE_SLASH:
                fsm.memory['cur_block_comment'] = [None, None]

        def do_slash_block_only(fsm):
            # print 'do_slash current_state=%s, symbol=\'%s\'' % (fsm.current_state, unicode(fsm.input_symbol))
            if fsm.current_state == STATE_NONE:
                fsm.memory['cur_block_comment'][0] = fsm.memory['cur_symbol_pos']
            elif fsm.current_state == STATE_STAR:
                fsm.memory['cur_block_comment'][1] = fsm.memory['cur_symbol_pos'] + 1
                fsm.memory['block_comments'].append(fsm.memory['cur_block_comment'])
                fsm.memory['cur_block_comment'] = [None, None]

        def do_slash_line_and_block(fsm):
            # print 'do_slash current_state=%s, symbol=\'%s\'' % (fsm.current_state, unicode(fsm.input_symbol))
            if fsm.current_state == STATE_NONE:
                fsm.memory['cur_line_comment'][0] = fsm.memory['cur_symbol_pos']
                fsm.memory['cur_block_comment'][0] = fsm.memory['cur_symbol_pos']
            elif fsm.current_state == STATE_STAR:
                fsm.memory['cur_block_comment'][1] = fsm.memory['cur_symbol_pos'] + 1
                fsm.memory['block_comments'].append(fsm.memory['cur_block_comment'])
                fsm.memory['cur_block_comment'] = [None, None]
            elif fsm.current_state == STATE_SLASH:
                fsm.memory['cur_block_comment'] = [None, None]

        def do_star(fsm):
            # print 'do_star current_state=%s, symbol=\'%s\'' % (fsm.current_state, unicode(fsm.input_symbol))
            if fsm.current_state == STATE_SLASH:
                fsm.memory['cur_line_comment'] = [None, None]

        def do_eol(fsm):
            # print 'do_eol current_state=%s, symbol=\'%s\'' % (fsm.current_state, unicode(fsm.input_symbol))
            if fsm.current_state == STATE_LINE_COMMENT:
                fsm.memory['cur_line_comment'][1] = fsm.memory['cur_symbol_pos'] + 1
                fsm.memory['line_comments'].append(fsm.memory['cur_line_comment'])
                fsm.memory['cur_line_comment'] = [None, None]

        self.java_fsm.set_default_transition(do_default, None)
        self.java_fsm.add_transition_any(STATE_NONE)

        # STATE_NONE
        do_slash_method = None
        if self.java_line_comment and self.java_block_comment:
            do_slash_method = do_slash_line_and_block
        elif self.java_line_comment:
            do_slash_method = do_slash_line_only
        elif self.java_block_comment:
            do_slash_method = do_slash_block_only
        self.java_fsm.add_transition('/', STATE_NONE, do_slash_method, STATE_SLASH)
        # STATE_SLASH
        self.java_fsm.add_transition('other', STATE_SLASH, do_other, STATE_NONE)
        self.java_fsm.add_transition('\n', STATE_SLASH, do_eol, STATE_NONE)
        if self.java_line_comment:
            self.java_fsm.add_transition('/', STATE_SLASH, do_slash_method, STATE_LINE_COMMENT)
        elif self.java_block_comment:
            self.java_fsm.add_transition('/', STATE_SLASH, do_slash_method, STATE_SLASH)
        if self.java_block_comment:
            self.java_fsm.add_transition('*', STATE_SLASH, do_star, STATE_BLOCK_COMMENT)
        elif self.java_line_comment:
            self.java_fsm.add_transition('*', STATE_SLASH, do_star, STATE_NONE)
        # STATE_LINE_COMMENT
        self.java_fsm.add_transition('\n', STATE_LINE_COMMENT, do_eol, STATE_NONE)
        # STATE_BLOCK_COMMENT
        self.java_fsm.add_transition('*', STATE_BLOCK_COMMENT, do_star, STATE_STAR)
        # STATE_STAR
        self.java_fsm.add_transition('other', STATE_STAR, do_other, STATE_BLOCK_COMMENT)
        self.java_fsm.add_transition('/', STATE_STAR, do_slash_method, STATE_NONE)
        self.java_fsm.add_transition('\n', STATE_STAR, do_eol, STATE_BLOCK_COMMENT)

        self.defined_symbols = '/*\n'

    def reset(self):
        self.java_fsm.reset()

    def process_buffer(self, buf, index_offset=0):
        """
        Feeds the buffer into FSM
        index_offset - is used when input data is split in chunks but there is a need to process that as one unit,
        in this case the result comment intervals would be applied for whole input stream
        """
        if self.custom_line_comment:
            loc_start = 0
            custom_line_comment_len = len(self.custom_line_comment)
            while loc_start != -1:
                if self.custom_comment_end_in_next:
                    loc_start = 0
                    self.custom_comment_end_in_next = False
                else:
                    loc_start = buf.find(self.custom_line_comment, loc_start)
                if loc_start != -1:
                    loc_end = buf.find('\n', loc_start)
                    if loc_end != -1:
                        self.custom_line_comments.append([index_offset + loc_start, index_offset + loc_end + 1])
                        loc_start = loc_end + 1
                    else:
                        self.custom_line_comments.append([index_offset + loc_start, index_offset + len(buf) + 1])
                        self.custom_comment_end_in_next = True
                        loc_start = custom_line_comment_len
                        break

        if self.java_line_comment or self.java_block_comment:
            for idx, symbol in enumerate(buf):
                self.java_fsm.memory['cur_symbol_pos'] = idx + index_offset
                self.java_fsm.process(symbol if symbol in self.defined_symbols else 'other')

    def skip_comments(self, chunk_buf, index_offset=0):
        self.process_buffer(chunk_buf, index_offset=index_offset)
        comments = self.get_comment_intervals()
        cur_block_comment = self.get_cur_block_comment()
        new_comments = []
        if comments:
            for c in comments:
                new_c = [c[0] - index_offset, c[1] - index_offset]
                if new_c[0] < 0:
                    new_c[0] = 0
                if new_c[1] < 0:
                    new_c[1] = 0
                new_comments.append(new_c)
        if cur_block_comment[0]:
            new_comments.append([cur_block_comment[0] - index_offset, len(chunk_buf)])
        self.clear_comment_intervals()
        if new_comments:
            new_buffer = ''
            end_comment_pos = 0
            for comment in new_comments:
                new_buffer += chunk_buf[end_comment_pos : comment[0]]
                # skipping empty lines in case of java block comments
                test_next_start = chunk_buf[comment[1]:comment[1] + 2]
                if '\r\n' == test_next_start:
                    end_comment_pos = comment[1] + 2
                elif '\r' == test_next_start[0:1] or '\n' == test_next_start[0:1]:
                    end_comment_pos = comment[1] + 1
                else:
                    end_comment_pos = comment[1]
            new_buffer += chunk_buf[end_comment_pos : len(chunk_buf)]
            return new_buffer
        return chunk_buf

    def get_cur_line_comment(self):
        return self.java_fsm.memory['cur_line_comment']

    def get_cur_block_comment(self):
        return self.java_fsm.memory['cur_block_comment']

    def get_comment_intervals(self):
        comments = self.java_fsm.memory['line_comments'] + self.java_fsm.memory['block_comments'] + \
               self.custom_line_comments
        comments = intervals_union([IInterval(c[0], c[1]) for c in comments])
        return comments

    def clear_comment_intervals(self):
        self.java_fsm.memory['line_comments'] = []
        self.java_fsm.memory['block_comments'] = []
        self.custom_line_comments = []


def remove_comments(buf, java_line_comment, java_block_comment, custom_line_comment):
    comment_detector = CommentsDetector(java_line_comment=java_line_comment,
                                        java_block_comment=java_block_comment,
                                        custom_line_comment=custom_line_comment)
    comment_detector.process_buffer(buf)
    comments = comment_detector.get_comment_intervals()
    cur_block_comment = comment_detector.get_cur_block_comment()
    if cur_block_comment[0]:
        comments.append([cur_block_comment[0], len(buf)])
    if comments:
        new_buffer = ''
        end_comment_pos = 0
        for comment in comments:
            new_buffer += buf[end_comment_pos : comment[0]]
            end_comment_pos = comment[1]
        new_buffer += buf[end_comment_pos : len(buf)]
        return new_buffer
    return buf


DEFAULT_IMPORT_PEEK_SIZE = 8192
DEFAULT_IMPORT_CHUNK_SIZE = 5*1024*1024  # 5 Mb
DEFAULT_IMPORT_MAX_SIZE = 4294967296  # 4 Gb
DEFAULT_IMPORT_PEEK_NLINES = 10


class GzipFileProcessor():

    TYPE = 'gzip'

    @staticmethod
    def read_preview_lines(fileobj, encoding,
                  import_peek_size=None, import_peek_nlines=None,
                  ignore_whitespaces=False, ignore_tabs=False,
                  single_line_comment=False, java_style_comments=False):
        gz = gzip.GzipFile(fileobj=fileobj, mode='rb')
        try:
            if import_peek_size:
                data = gz.read(import_peek_size)
            else:
                data = gz.read(DEFAULT_IMPORT_PEEK_SIZE)
            data = unicode(data, encoding, errors='ignore')
            if java_style_comments or single_line_comment:
                data = remove_comments(data,
                                       java_line_comment=java_style_comments,
                                       java_block_comment=java_style_comments,
                                       custom_line_comment=single_line_comment)
            if ignore_whitespaces:
                data = data.replace(' ', '')
            if ignore_tabs:
                data = data.replace('\t', '')
        except IOError:
            return None
        except UnicodeError:
            return None
        if import_peek_nlines:
            return [s for s in data.splitlines() if s.strip()][:-1][:import_peek_nlines]
        else:
            return [s for s in data.splitlines() if s.strip()][:-1][:DEFAULT_IMPORT_PEEK_NLINES]

    @staticmethod
    def read_in_chunks(fs, path, encoding):
        src_file_obj = fs.open(path, mode='r')
        gz = gzip.GzipFile(fileobj=src_file_obj, mode='rb')
        align_rest = ''
        while True:
            chunk = gz.read(DEFAULT_IMPORT_CHUNK_SIZE)
            if chunk:
                chunk_len = len(chunk)
                chunk = align_rest + chunk
                if chunk_len < DEFAULT_IMPORT_CHUNK_SIZE:  # last chunk
                    chunk = unicode('\n'.join([s for s in chunk.splitlines() if s.strip()]), encoding, errors='ignore')
                else:
                    lines = chunk.splitlines()
                    if 1 == len(lines):
                        raise Exception('File could not be read in chunks: default chunk size is %s [bytes]'
                                        % DEFAULT_IMPORT_CHUNK_SIZE)
                    align_rest = lines[-1]
                    if chunk[-1] == '\n' or chunk[-1] == '\r':
                        align_rest += '\n'
                    chunk = unicode('\n'.join([s for s in lines[:-1] if s.strip()]), encoding, errors='ignore')
                yield chunk
            else:
                src_file_obj.close()
                return
        src_file_obj.close()

    @staticmethod
    def append_chunk(fs, path, data, encoding):
        dest_file_obj = fs.open(path, mode='w')
        gz = gzip.GzipFile(fileobj=dest_file_obj, mode='wb')
        # data = data.encode(encoding, 'ignore')
        gz.write(data)
        dest_file_obj.close()

    @staticmethod
    def remove_comments_from_file(fs, src_path, dest_path, java_line_comment, java_block_comment, custom_line_comment):
        comment_detector = CommentsDetector(java_line_comment=java_line_comment,
                                            java_block_comment=java_block_comment,
                                            custom_line_comment=custom_line_comment)
        src_file_obj = fs.open(src_path, mode='r')
        src_gz = gzip.GzipFile(fileobj=src_file_obj, mode='rb')
        offset = 0
        while True:
            chunk = fs.read(src_path, offset, DEFAULT_IMPORT_CHUNK_SIZE)
            if chunk:
                chunk_len = len(chunk)
                comment_detector.process_buffer(chunk, index_offset=offset)
                offset += chunk_len
            else:
                break

        comments = comment_detector.get_comment_intervals()
        if comments:
            fs.create(dest_path, overwrite=True, permission=0777)
            dest_file_obj = fs.open(src_path, mode='w')
            dest_gz = gzip.GzipFile(fileobj=dest_file_obj, mode='wb')
            src_size = offset
            content_to_copy = [x for x in range(0, src_size, DEFAULT_IMPORT_CHUNK_SIZE) + [src_size]]
            if len(content_to_copy) > 1:
                content_to_copy = [IInterval(content_to_copy[i], c) for i, c in enumerate(content_to_copy[1:])]
            else:
                content_to_copy = [IInterval(0, src_size)]
            for comment in comments:
                content_to_copy = intervals_subtraction(content_to_copy, comment)
            for chunk_to_copy in content_to_copy:
                src_gz.seek(chunk_to_copy.start)
                sub_chunk = src_gz.read(chunk_to_copy.end - chunk_to_copy.start)
                if sub_chunk:
                    dest_gz.write(sub_chunk)
            src_file_obj.close()
            dest_file_obj.close()
            return dest_path
        src_file_obj.close()
        return src_path


class TextFileProcessor():
    TYPE = 'text'

    @staticmethod
    def read_preview_lines(fileobj, encoding,
                  import_peek_size=None, import_peek_nlines=None,
                  ignore_whitespaces=False, ignore_tabs=False,
                  single_line_comment=False, java_style_comments=False):
        try:
            if import_peek_size:
                data = fileobj.read(import_peek_size)
            else:
                data = fileobj.read(DEFAULT_IMPORT_PEEK_SIZE)
            data = unicode(data, encoding, errors='ignore')
            if java_style_comments or single_line_comment:
                data = remove_comments(data,
                                        java_line_comment=java_style_comments,
                                        java_block_comment=java_style_comments,
                                        custom_line_comment=single_line_comment)
            if ignore_whitespaces:
                data = data.replace(' ', '')
            if ignore_tabs:
                data = data.replace('\t', '')
        except IOError:
            return None
        except UnicodeError:
            return None
        if import_peek_nlines:
            return [s for s in data.splitlines() if s.strip()][:-1][:DEFAULT_IMPORT_PEEK_NLINES]
        else:
            return [s for s in data.splitlines() if s.strip()][:-1][:import_peek_nlines]

    @staticmethod
    def read_in_chunks(fs, path, encoding):
        offset = 0
        while True:
            chunk = fs.read(path, offset, DEFAULT_IMPORT_CHUNK_SIZE)
            if chunk:
                chunk_len = len(chunk)
                if chunk_len < DEFAULT_IMPORT_CHUNK_SIZE:  # last chunk
                    chunk = unicode('\n'.join([s for s in chunk.splitlines() if s.strip()]), encoding, errors='ignore')
                else:
                    lines = chunk.splitlines()
                    if 1 == len(lines):
                        raise Exception('File could not be read in chunks: default chunk size is %s [bytes]'
                                        % DEFAULT_IMPORT_CHUNK_SIZE)
                    chunk_len -= len(lines[-1])
                    chunk = unicode('\n'.join([s for s in lines[:-1] if s.strip()]), encoding, errors='ignore')
                offset += chunk_len
                yield chunk
            else:
                return

    @staticmethod
    def append_chunk(fs, path, data, encoding):
        data = data.encode(encoding, 'ignore')
        fs.append(path, data)

    @staticmethod
    def remove_comments_from_file(fs, src_path, dest_path, java_line_comment, java_block_comment, custom_line_comment):
        comment_detector = CommentsDetector(java_line_comment=java_line_comment,
                                        java_block_comment=java_block_comment,
                                        custom_line_comment=custom_line_comment)

        offset = 0
        while True:
            chunk = fs.read(src_path, offset, DEFAULT_IMPORT_CHUNK_SIZE)
            if chunk:
                chunk_len = len(chunk)
                comment_detector.process_buffer(chunk, index_offset=offset)
                offset += chunk_len
            else:
                break

        comments = comment_detector.get_comment_intervals()
        if comments:
            fs.create(dest_path, overwrite=True, permission=0777)
            src_stats = fs.stats(src_path)
            src_size = src_stats['size']
            content_to_copy = [x for x in range(0, src_size, DEFAULT_IMPORT_CHUNK_SIZE) + [src_size]]
            if len(content_to_copy) > 1:
                content_to_copy = [IInterval(content_to_copy[i], c) for i, c in enumerate(content_to_copy[1:])]
            else:
                content_to_copy = [IInterval(0, src_size)]
            for comment in comments:
                content_to_copy = intervals_subtraction(content_to_copy, comment)
            for chunk_to_copy in content_to_copy:
                sub_chunk = fs.read(src_path, chunk_to_copy.start, chunk_to_copy.end - chunk_to_copy.start)
                if sub_chunk:
                    fs.append(dest_path, sub_chunk)
            return dest_path
        return src_path

def excel_col_to_index(col_name):
    index = 0
    div = 0
    for i, c in enumerate(col_name[::-1]):
        if c in string.ascii_letters:
            index += (ord(c.upper()) - ord('A') + 1) * 26 ** (i - div)
        else:
            div += 1
    return index - 1


def index_to_excel_col(index):
    col_name = ''
    current = index
    while current >= 0:
        remainder = current % 26
        col_name = chr(ord('A') + remainder) + col_name
        current = current / 26 - 1
    return col_name


def excel_range_to_indexes(range_str):
    """
    Converts input string range in excel format 'A3:B6' to set of zero-based indexes
        like ((col_min_idx, col_max_idx), (row_min_idx, row_max_idx))
    """
    excel_range = re.match(r'^(?P<col_min_idx>[a-zA-Z]+)(?P<row_min_idx>\d+):(?P<col_max_idx>[a-zA-Z]+)(?P<row_max_idx>\d+$)',
                     range_str)
    if excel_range:
        col_min_idx = excel_col_to_index(excel_range.group('col_min_idx'))
        row_min_idx = int(excel_range.group('row_min_idx'))
        row_min_idx = row_min_idx - 1 if row_min_idx > 0 else 0
        col_max_idx = excel_col_to_index(excel_range.group('col_max_idx'))
        row_max_idx = int(excel_range.group('row_max_idx'))
        row_max_idx = row_max_idx - 1 if row_max_idx > 0 else 0
        return ((col_min_idx if col_min_idx < col_max_idx else col_max_idx,
                row_min_idx if row_min_idx < row_max_idx else row_max_idx),
                (col_max_idx if col_max_idx >= col_min_idx else col_min_idx,
                row_max_idx if row_max_idx >= row_min_idx else row_min_idx))
    return None


def showable_cell_value(celltype, cellvalue, datemode):
    if celltype == xlrd.XL_CELL_DATE:
        try:
            dt = xlrd.xldate_as_tuple(cellvalue, datemode)
            if len(dt) >= 6:
                try:
                    showval = datetime(*(dt[0:6])).isoformat(sep=' ')
                except ValueError:
                    try:
                        # it means that date is not valid and as result will be returned a string reflected only time
                        showval = unicode(time(*(dt[3:6])))
                    except ValueError:
                        showval = ''
            else:
                showval = ''
        except xlrd.XLDateError:
            showval = ''
    elif celltype == xlrd.XL_CELL_NUMBER:
        if 0 == cellvalue - int(cellvalue):
            showval = int(cellvalue)
        else:
            showval = cellvalue
    elif celltype == xlrd.XL_CELL_ERROR:
        showval = ''
    else:
        showval = cellvalue
    return showval

class XlsFileProcessor():
    TYPE = 'xls'

    @staticmethod
    def open(fileobj, max_size=None):
        try:
            if max_size:
                data = fileobj.read(max_size)
            else:
                data = fileobj.read(DEFAULT_IMPORT_MAX_SIZE)
        except IOError:
            return None
        return xlrd.open_workbook(file_contents=data)

    @staticmethod
    def get_sheet_list(xls_fileobj):
        return [xls_fileobj.sheet_names()[idx] for idx in range(xls_fileobj.nsheets)]

    @staticmethod
    def get_sheet_name(xls_fileobj, sheet_index):
        return xls_fileobj.sheet_names()[sheet_index]

    @staticmethod
    def get_column_names(xls_fileobj, sheet_index=0, cell_range=None):
        sh = xls_fileobj.sheet_by_index(sheet_index)
        col_min_idx = 0
        col_max_idx = sh.ncols - 1
        if cell_range is not None and cell_range != '' and cell_range != '*':
            excel_range = excel_range_to_indexes(cell_range)
            if excel_range is not None:
                col_min_idx = excel_range[0][0]
                col_max_idx = excel_range[1][0]
        return [index_to_excel_col(rx) for rx in range(col_min_idx, col_max_idx + 1)]

    @staticmethod
    def get_scope_data(xls_fileobj, scope_strg, cell_range=None, row_start_idx=None, row_end_idx=None):
        """
        scope_strg - sheet name or '*' that means all sheets
        cell_range - range string in an excel style 'B1:D10'
        row_start_idx - row start index in result data when scope_strg and cell_range are applied
        row_end_idx - row end index in result data when scope_strg and cell_range are applied
        """
        try:
            qscope = int(scope_strg)
        except ValueError:
            if scope_strg == "*":
                qscope = None  # means 'all'
            else:
                # so assume it's a sheet name ...
                qscope = xls_fileobj.sheet_names().index(scope_strg)
        data = []
        datemode = xls_fileobj.datemode
        for sh_idx in range(xls_fileobj.nsheets):
            if qscope is None or sh_idx == qscope:
                sh = xls_fileobj.sheet_by_index(sh_idx)
                if sh.ncols == 0 or sh.nrows == 0:
                    continue
                col_min_idx = 0
                col_max_idx = sh.ncols - 1
                row_min_idx = 0
                row_max_idx = sh.nrows - 1
                if cell_range is not None and cell_range != '' and cell_range != '*':
                    excel_range = excel_range_to_indexes(cell_range)
                    if excel_range is not None:
                        (new_col_min_idx, new_row_min_idx), (new_col_max_idx, new_row_max_idx) = excel_range
                        col_intersection = intervals_intersection([IInterval(col_min_idx, col_max_idx),
                                                                   IInterval(new_col_min_idx, new_col_max_idx)])
                        row_intersection = intervals_intersection([IInterval(row_min_idx, row_max_idx),
                                                                   IInterval(new_row_min_idx, new_row_max_idx)])
                        if not col_intersection or not row_intersection:
                            continue
                        else:
                            col_min_idx = col_intersection[0].start
                            col_max_idx = col_intersection[0].end
                            row_min_idx = row_intersection[0].start
                            row_max_idx = row_intersection[0].end

                if row_start_idx is not None and row_end_idx is not None:
                    row_intersection = intervals_intersection([IInterval(row_min_idx, row_max_idx),
                                                               IInterval(row_min_idx + row_start_idx,
                                                                         row_min_idx + row_end_idx)])
                    if not row_intersection:
                        continue
                    else:
                        row_min_idx = row_intersection[0].start
                        row_max_idx = row_intersection[0].end

                for rowx in range(row_min_idx, row_max_idx + 1):
                    row = []
                    for colx in range(col_min_idx, col_max_idx + 1):
                        cty = sh.cell_type(rowx, colx)
                        cval = sh.cell_value(rowx, colx)
                        row.append(showable_cell_value(cty, cval, datemode))
                    data.append(row)
        return data

    @staticmethod
    def write_to_dsv_gzip(fs, xls_fileobj, dest_path, data, field_terminator, newline_terminator='\n'):
        dest_file_obj = fs.open(dest_path, mode='w')
        gz = gzip.GzipFile(fileobj=dest_file_obj, mode='wb')
        data_to_store = []
        for row in data:
            new_row = []
            for field in row:
                new_row.append(unicode(field).encode('utf-8', "ignore").replace(field_terminator.decode('string_escape'), ''))
            data_to_store.append(field_terminator.decode('string_escape').join(new_row))
        gz.write(newline_terminator.join(data_to_store))
        dest_file_obj.close()