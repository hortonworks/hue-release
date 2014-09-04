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

from django import forms
from django.forms.fields import ChoiceField
from desktop.lib.django_forms import simple_formset_factory, DependencyAwareForm
from desktop.lib.django_forms import ChoiceOrOtherField, MultiForm, SubmitButton
from hcatalog import common
from hcatalog.common import UnicodeEncodingField
from hcat_client import HCatClient
import filebrowser.forms


# Note, struct is not currently supported.  (Because it's recursive, for example.)
HIVE_TYPES = \
    ("string", "tinyint", "smallint", "int", "bigint", "boolean", "float", "double", "timestamp", "decimal", "binary",
     "array", "map")
HIVE_PRIMITIVE_TYPES = \
    ("string", "tinyint", "smallint", "int", "bigint", "boolean", "float", "double", "timestamp", "decimal", "binary")

IMPORT_FILE_TYPE_CHOICES = [
    ('text', 'Text file'),
    ('spreadsheet', 'Spreadsheet file'),
    # ('msaccess', 'MS Access'),
    ('none', 'None'),
]

IMPORT_FILE_TYPE_TEXT = IMPORT_FILE_TYPE_CHOICES[0][0]
IMPORT_FILE_TYPE_SPREADSHEET = IMPORT_FILE_TYPE_CHOICES[1][0]
# IMPORT_FILE_TYPE_MS_ACCESS = IMPORT_FILE_TYPE_CHOICES[2][0]
IMPORT_FILE_TYPE_NONE = IMPORT_FILE_TYPE_CHOICES[2][0]

class ImportFileTypeField(ChoiceField):
    """Used for selecting import file type."""
    def __init__(self, initial=None, *args, **kwargs):
        ChoiceField.__init__(self, IMPORT_FILE_TYPE_CHOICES, initial, *args, **kwargs)

    def clean(self, value):
        return value


def query_form():
    """Generates a multi form object for queries."""
    return MultiForm(
        query=HQLForm,
        settings=SettingFormSet,
        file_resources=FileResourceFormSet,
        functions=FunctionFormSet,
        saveform=SaveForm)


class DbForm(forms.Form):
    database = forms.ChoiceField(required=False,
                                 label='',
                                 choices=(('default', 'default'),),
                                 initial=0,
                                 widget=forms.widgets.Select(attrs={'class': 'span6'}))

    def __init__(self, *args, **kwargs):
        databases = kwargs.pop('databases')
        super(DbForm, self).__init__(*args, **kwargs)
        self.fields['database'].choices = ((db, db) for db in databases)


class SaveForm(forms.Form):
    """Used for saving query design and report design."""
    name = forms.CharField(required=False,
                           max_length=64,
                           help_text='Change the name to save as a new design')
    desc = forms.CharField(required=False, max_length=1024, label="Description")
    save = forms.BooleanField(widget=SubmitButton, required=False)
    saveas = forms.BooleanField(widget=SubmitButton, required=False)

    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.fields['save'].label = 'Save'
        self.fields['save'].widget.label = 'Save'
        self.fields['saveas'].label = 'Save As'
        self.fields['saveas'].widget.label = 'Save As'

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        return name

    def clean(self):
        if self.errors:
            return
        save = self.cleaned_data.get('save')
        name = self.cleaned_data.get('name')
        if save and len(name) == 0:
            # Bother with name if we're saving
            raise forms.ValidationError('Please enter a name')
        return self.cleaned_data

    def set_data(self, name, desc=''):
        """Set the name and desc programmatically"""
        data2 = self.data.copy()
        data2[self.add_prefix('name')] = name
        data2[self.add_prefix('desc')] = desc
        self.data = data2


class HQLForm(forms.Form):
    query = forms.CharField(label="Query Editor",
                            required=True,
                            widget=forms.Textarea(attrs={'class': 'beeswax_query'}))
    is_parameterized = forms.BooleanField(required=False, initial=True)
    email_notify = forms.BooleanField(required=False, initial=False)


class FunctionForm(forms.Form):
    name = forms.CharField(required=True)
    class_name = forms.CharField(required=True)


FunctionFormSet = simple_formset_factory(FunctionForm)


class FileResourceForm(forms.Form):
    type = forms.ChoiceField(required=True,
                             choices=[
                                 ("JAR", "jar"),
                                 ("ARCHIVE", "archive"),
                                 ("FILE", "file"),
                             ], help_text="Resources to upload with your Hive job." +
                                          "  Use 'jar' for UDFs.  Use file and archive for "
                                          "side files and MAP/TRANSFORM using.  Paths are on HDFS."
    )
    # TODO(philip): Could upload files here, too.  Or merely link
    # to upload utility?
    path = forms.CharField(required=True, help_text="Path to file on HDFS.")


FileResourceFormSet = simple_formset_factory(FileResourceForm)


class SettingForm(forms.Form):
    # TODO: There are common settings that should be always exposed?
    key = forms.CharField()
    value = forms.CharField()


SettingFormSet = simple_formset_factory(SettingForm)


# In theory, there are only 256 of these...
TERMINATOR_CHOICES = [(hive_val, desc) for hive_val, desc, _ in common.TERMINATORS]


class CreateTableForm(DependencyAwareForm):
    """
    Form used in the create table page
    """
    dependencies = []

    # Basic Data
    name = common.HiveIdentifierField(label="Table Name", required=True)
    comment = forms.CharField(label="Description", required=False)

    # Row Formatting
    row_format = forms.ChoiceField(required=True,
                                   choices=common.to_choices(["Delimited", "SerDe"]),
                                   initial="Delimited")

    # Delimited Row
    # These initials are per LazySimpleSerDe.DefaultSeparators
    field_terminator = ChoiceOrOtherField(required=False, initial=TERMINATOR_CHOICES[0][0],
                                          choices=TERMINATOR_CHOICES)
    collection_terminator = ChoiceOrOtherField(required=False, initial=TERMINATOR_CHOICES[1][0],
                                               choices=TERMINATOR_CHOICES)
    map_key_terminator = ChoiceOrOtherField(required=False, initial=TERMINATOR_CHOICES[2][0],
                                            choices=TERMINATOR_CHOICES)
    dependencies += [
        ("row_format", "Delimited", "field_terminator"),
        ("row_format", "Delimited", "collection_terminator"),
        ("row_format", "Delimited", "map_key_terminator"),
    ]

    # Serde Row
    serde_name = forms.CharField(required=False, label="SerDe Name")
    serde_properties = forms.CharField(
        required=False,
        help_text="Comma-separated list of key-value pairs, eg., 'p1=v1, p2=v2'")

    dependencies += [
        ("row_format", "SerDe", "serde_name"),
        ("row_format", "SerDe", "serde_properties"),
    ]

    # File Format
    file_format = forms.ChoiceField(required=False, initial="TextFile",
                                    choices=common.to_choices(["TextFile", "SequenceFile", "InputFormat"]),
                                    widget=forms.RadioSelect)
    input_format_class = forms.CharField(required=False, label="InputFormat Class")
    output_format_class = forms.CharField(required=False, label="OutputFormat Class")

    dependencies += [
        ("file_format", "InputFormat", "input_format_class"),
        ("file_format", "InputFormat", "output_format_class"),
    ]

    # External?
    use_default_location = forms.BooleanField(required=False, initial=True,
                                              label="Use default location")
    external_location = forms.CharField(required=False, help_text="Path to HDFS directory or file of table data.")

    dependencies += [
        ("use_default_location", False, "external_location")
    ]

    def __init__(self, *args, **kwargs):
        DependencyAwareForm.__init__(self, *args, **kwargs)
        self.table_list = []

    def clean_field_terminator(self):
        return _clean_terminator(self.cleaned_data.get('field_terminator'))

    def clean_collection_terminator(self):
        return _clean_terminator(self.cleaned_data.get('collection_terminator'))

    def clean_map_key_terminator(self):
        return _clean_terminator(self.cleaned_data.get('map_key_terminator'))

    def clean_name(self):
        return _clean_tablename(self.table_list, self.cleaned_data['name'])


class ChoiceFieldExtended(ChoiceField):

    def validate(self, value):
        pass


class CreateTableFromFileForm(forms.Form):
    """
    Form used in the create table from file page
    """

    # Basic Data
    name = common.HiveIdentifierField(label="Table Name", required=False)
    comment = forms.CharField(label="Description", required=False)

    path = filebrowser.forms.PathField(label="Input File")

    # csv/tsv files
    encoding = UnicodeEncodingField()
    delimiter = ChoiceOrOtherField(required=False, initial=TERMINATOR_CHOICES[0][0], choices=TERMINATOR_CHOICES)
    replace_delimiter_with = ChoiceOrOtherField(required=False, initial=TERMINATOR_CHOICES[0][0], choices=TERMINATOR_CHOICES,
                                          label="Replace delimiter with")
    read_column_headers = forms.BooleanField(required=False, initial=True,
                                             label="Read column headers",
                                             help_text="")
    import_data = forms.BooleanField(required=False, initial=True,
                                     label="Import data",
                                     help_text="")
    autodetect_delimiter = forms.BooleanField(required=False, initial=True,
                                            label="Autodetect delimiter",
                                            help_text="")
    ignore_whitespaces = forms.BooleanField(required=False, initial=False,
                                            label="Ignore whitespaces",
                                            help_text="")
    ignore_tabs = forms.BooleanField(required=False, initial=False,
                                     label="Ignore tabs",
                                     help_text="")
    single_line_comment = forms.CharField(label="Single line comment", required=False)
    java_style_comments = forms.BooleanField(required=False, initial=False,
                                             label="Java-style comments",
                                             help_text="")

    apply_excel_dialect = forms.BooleanField(required=False, initial=True,
                                             label="Read column headers",
                                             help_text="")

    # xls/xlsx files
    xls_sheet = ChoiceFieldExtended(label="Sheet", required=False)
    xls_cell_range = forms.CharField(label="Cell range", required=False)
    xls_read_column_headers = forms.BooleanField(required=False, initial=True,
                                             label="Read column headers",
                                             help_text="")


def _clean_tablename(table_list, name):
    if name in table_list:
        raise forms.ValidationError('Table "%s" already exists' % (name,))
    return name


def _clean_terminator(val):
    if val is not None and len(val.decode('string_escape')) != 1:
        raise forms.ValidationError('Terminator must be exactly one character')
    return val


class PartitionTypeForm(forms.Form):
    column_name = common.HiveIdentifierField(required=True)
    column_type = forms.ChoiceField(required=True, choices=common.to_choices(sorted(HIVE_PRIMITIVE_TYPES)),
                                    initial=HIVE_PRIMITIVE_TYPES[0])


class ColumnTypeForm(DependencyAwareForm):
    """
    Form used to specify a column during table creation
    """
    dependencies = [
        ("column_type", "array", "array_type"),
        ("column_type", "map", "map_key_type"),
        ("column_type", "map", "map_value_type"),
    ]
    column_name = common.HiveIdentifierField(required=True)
    column_type = forms.ChoiceField(required=True,
                                    choices=common.to_choices(sorted(HIVE_TYPES)),
                                    initial=HIVE_TYPES[0])
    array_type = forms.ChoiceField(required=False,
                                   choices=common.to_choices(sorted(HIVE_PRIMITIVE_TYPES)),
                                   initial=HIVE_PRIMITIVE_TYPES[0],
                                   label="Array Value Type")
    map_key_type = forms.ChoiceField(required=False,
                                     choices=common.to_choices(sorted(HIVE_PRIMITIVE_TYPES)),
                                     initial=HIVE_PRIMITIVE_TYPES[0],
                                     help_text="Specify if column_type is map.")
    map_value_type = forms.ChoiceField(required=False,
                                       choices=common.to_choices(sorted(HIVE_PRIMITIVE_TYPES)),
                                       initial=HIVE_PRIMITIVE_TYPES[0],
                                       help_text="Specify if column_type is map.")


ColumnTypeFormSet = simple_formset_factory(ColumnTypeForm, initial=[{}], add_label="add a column")
# Default to no partitions
PartitionTypeFormSet = simple_formset_factory(PartitionTypeForm, add_label="add a partition")


class LoadDataForm(forms.Form):
    """Form used for loading data into an existing table."""
    path = filebrowser.forms.PathField(label="Path")
    overwrite = forms.BooleanField(required=False, initial=False, label="Overwrite?")


    def __init__(self, table_obj, *args, **kwargs):
        super(LoadDataForm, self).__init__(*args, **kwargs)
        self.partition_columns = dict()
        for i, column in enumerate(table_obj['partitionKeys']):
            # We give these numeric names because column names
            # may be unpleasantly arbitrary.
            name = "partition_%d" % i
            char_field = forms.CharField(required=True,
                                         label="%s (partition key with type %s)" % (column['name'], column['type']))
            self.fields[name] = char_field
            self.partition_columns[name] = column['name']


def _clean_databasename(database_list, db_name):
    if db_name in database_list:
        raise forms.ValidationError('Database "%(db_name)s" already exists' % {'db_name': db_name})
    return db_name


class CreateDatabaseForm(DependencyAwareForm):
    """
    Form used in the create database page
    """
    dependencies = []

    # Basic Data
    db_name = common.HiveIdentifierField(label="Database Name", required=True)
    comment = forms.CharField(label="Description", required=False)

    # External if not true
    use_default_location = forms.BooleanField(required=False, initial=True, label="Use default location")
    external_location = forms.CharField(required=False, help_text="Path to HDFS directory or file of database data.")

    dependencies += [("use_default_location", False, "external_location")]

    def __init__(self, *args, **kwargs):
        DependencyAwareForm.__init__(self, *args, **kwargs)
        self.database_list = []

    def clean_db_name(self):
        return _clean_databasename(self.database_list, self.cleaned_data['db_name'])
