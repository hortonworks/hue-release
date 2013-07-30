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
from hcatalog.views import _get_table_list, _get_last_database
from hcat_client import HCatClient
from beeswax.server import dbms
from desktop.context_processors import get_app_name

import logging

LOG = logging.getLogger(__name__)


def create_table(request, database=None):
    """Create a table by specifying its attributes manually"""
    if database is None:
        database = _get_last_database(request, database)
    form = MultiForm(
        table=hcatalog.forms.CreateTableForm,
        columns=hcatalog.forms.ColumnTypeFormSet,
        partitions=hcatalog.forms.PartitionTypeFormSet)
    db = dbms.get(request.user)
    databases = db.get_databases()
    db_form = hcatalog.forms.DbForm(initial={'database': database}, databases=databases)
    error = None
    if request.method == "POST":
        form.bind(request.POST)
        form.table.table_list = _get_table_list(request)
        if form.is_valid() and 'createTable' in request.POST:
            try:
                columns = [f.cleaned_data for f in form.columns.forms]
                column_names = [col["column_name"] for col in columns]
                isTableValid, tableValidErrMsg = hcatalog.common.validateHiveTable(column_names)
                if not isTableValid:
                    raise Exception(tableValidErrMsg)
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
                hcat_cli = HCatClient(request.user.username)
                hcat_cli.create_table(database, tablename, proposed_query)
                databases = hcat_cli.get_databases(like="*")
                db_form = hcatalog.forms.DbForm(initial={'database': database}, databases=databases)
                return render("show_tables.mako", request, {
                    'database': database,
                    'db_form': db_form,
                })
            except Exception as ex:
                error = ex.message
    else:
        form.bind()
    return render("create_table_manually.mako", request, dict(
        database=database,
        db_form=db_form,
        table_form=form.table,
        columns_form=form.columns,
        partitions_form=form.partitions,
        error=error,
    ))
