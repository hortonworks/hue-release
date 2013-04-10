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
Views & controls for creating tables
"""

from desktop.lib import django_mako, i18n
from desktop.lib.django_util import render
from desktop.lib.django_forms import MultiForm

import hcatalog.common
import hcatalog.forms
from hcatalog.views import _get_table_list
from hcat_client import hcat_client
from desktop.context_processors import get_app_name

import logging

LOG = logging.getLogger(__name__)


def create_table(request, database='default'):
    """Create a table by specifying its attributes manually"""
    form = MultiForm(
        table=hcatalog.forms.CreateTableForm,
        columns=hcatalog.forms.ColumnTypeFormSet,
        partitions=hcatalog.forms.PartitionTypeFormSet)
    error = None
    if request.method == "POST":
        form.bind(request.POST)
        form.table.table_list = _get_table_list(request)
        if form.is_valid() and 'createTable' in request.POST:
            try:
                columns = [f.cleaned_data for f in form.columns.forms]
                partition_columns = [f.cleaned_data for f in form.partitions.forms]
                proposed_query = django_mako.render_to_string("create_table_statement.mako",
                                                              {
                                                                  'table': form.table.cleaned_data,
                                                                  'columns': columns,
                                                                  'partition_columns': partition_columns
                                                              })
                # Mako outputs bytestring in utf8
                proposed_query = proposed_query.decode('utf-8')
                tablename = form.table.cleaned_data['name']
                hcat_client().create_table_by_templeton(database, tablename, proposed_query)
                tables = _get_table_list(request)
                return render("show_tables.mako", request, dict(database=database, tables=tables,))
            except Exception as ex:
                error = ex.message
    else:
        form.bind()
    return render("create_table_manually.mako", request, dict(
        database=database,
        table_form=form.table,
        columns_form=form.columns,
        partitions_form=form.partitions,
        error=error,
    ))
