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

"""
Common utils for hcatalog.
"""

import re
from django.forms.fields import ChoiceField
import desktop.lib.i18n

from django import forms

# Hive tables restrictions from hive-schema-0.10.0.mysql.sql
HIVE_COLUMN_NAME_MAX_LEN = 128

HIVE_IDENTIFER_REGEX = re.compile("^[a-zA-Z0-9]\w*$")

DL_FORMATS = ['csv', 'xlsx']

SELECTION_SOURCE = ['', 'table', 'constant', ]

AGGREGATIONS = ['', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX']

JOIN_TYPES = ['', 'LEFT OUTER JOIN', 'RIGHT OUTER JOIN', 'FULL OUTER JOIN', 'JOIN']

SORT_OPTIONS = ['', 'ascending', 'descending']

RELATION_OPS_UNARY = ['IS NULL', 'IS NOT NULL', 'NOT']

RELATION_OPS = ['=', '<>', '<', '<=', '>', '>='] + RELATION_OPS_UNARY

TERMINATORS = [
    # (hive representation, description, ascii value)
    (r'\001', r"'^A' (\001)", 1),
    (r'\002', r"'^B' (\002)", 2),
    (r'\003', r"'^C' (\003)", 3),
    (r'\t', r"Tab (\t)", 9),
    (',', "Comma (,)", 44),
    (' ', "Space", 32),
]


def validateHiveTable(column_name_list):

    # validation column names
    for col in column_name_list:
        if len(col) > HIVE_COLUMN_NAME_MAX_LEN:
            error = "The column name '%s' is too long (max column name length is %d)." % (unicode(col),
                                                                                          HIVE_COLUMN_NAME_MAX_LEN)
            return False, error
    return True, None


def to_choices(x):
    """
    Maps [a, b, c] to [(a,a), (b,b), (c,c)].
    Useful for making ChoiceField's.
    """
    return [(y, y) for y in x]


class HiveIdentifierField(forms.RegexField):
    """
    Corresponds to 'Identifier' in Hive.g (Hive's grammar)
    """

    def __init__(self, *args, **kwargs):
        kwargs['regex'] = HIVE_IDENTIFER_REGEX
        super(HiveIdentifierField, self).__init__(*args, **kwargs)


class UnicodeEncodingField(ChoiceField):
    """
    The cleaned value of the field is the actual encoding, not a tuple
    """
    CHOICES = [
        ('utf-8', 'Unicode UTF8'),
        ('utf-16', 'Unicode UTF16'),
        ('latin_1', 'Western ISO-8859-1'),
        ('latin_9', 'Western ISO-8859-15'),
        ('cyrillic', 'Cryrillic'),
        ('arabic', 'Arabic'),
        ('greek', 'Greek'),
        ('hebrew', 'Hebrew'),
        ('shift_jis', 'Japanese (Shift-JIS)'),
        ('euc-jp', 'Japanese (EUC-JP)'),
        ('iso2022_jp', 'Japanese (ISO-2022-JP)'),
        ('euc-kr', 'Korean (EUC-KR)'),
        ('iso2022-kr', 'Korean (ISO-2022-KR)'),
        ('gbk', 'Chinese Simplified (GBK)'),
        ('big5hkscs', 'Chinese Traditional (Big5-HKSCS)'),
        ('ascii', 'ASCII'),
    ]

    def __init__(self, initial=None, *args, **kwargs):
        ChoiceField.__init__(self, UnicodeEncodingField.CHOICES, initial, *args, **kwargs)

    def clean(self, value):
        encoding = value
        if encoding and not desktop.lib.i18n.validate_encoding(encoding):
            raise forms.ValidationError("'%s' encoding is not available" % (encoding,))
        return encoding