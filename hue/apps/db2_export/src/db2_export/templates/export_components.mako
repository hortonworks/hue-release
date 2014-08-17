<%!
from desktop.lib.django_util import extract_field_data
from django.forms.widgets import TextInput
from db2_export.step_info import StepInfo
from db2_export.number import human_size
from django.utils.translation import ugettext as _
import json
%>

<%def name="open_form(id)">
  <form action="${url(app_name + ':export_results', id=id)}" method="POST" id="mainForm" class="form-horizontal"> ${ csrf_token_field | n }
</%def>

<%def name="close_form()">
</form>
</%def>

<%def name="cancel_button(id, content='Cancel')">
  <a href="${url(app_name + ':watch_query', id=id, download_format=None)}" class="btn">${content}</a>
</%def>

<%def name="step(title, step, target=None)">
  <%
    extra = { StepInfo.SUBMIT_STEP: step }
    if target != None:
      extra[StepInfo.TARGET_STEP] = target
    extra_data = json.dumps(extra)
  %>
  <a id=${"step%s" % (target+1,)} class="step" href="#" }>${title}</a>
</%def>

<%def name="next_button(step, content='Next')">
  <%
    extra_data = json.dumps({ StepInfo.SUBMIT_STEP: step })
  %>
  <input type="hidden" class="hide" name="${ StepInfo.SUBMIT_STEP }" value="${ step }" />
  <input type="submit" name="export-submit" class="btn primary" value="${ content }"/>
</%def>

<%def name="export_buttons(id)">
  <div class="wizard-button">
    ${cancel_button(id, 'Back to result')}
  </div>
</%def>

<%def name="wizard_buttons(id, wizard)">
  <div class="form-actions">
    ${cancel_button(id)}
    ${next_button(wizard.step_index())}
  </div>
</%def>

<%def name="hide_formset(formset)">
  %if columns.total_form_count() > 0:
    %for form in formset.forms:
      ${unicode(hide_form(form)) | n}
    %endfor
  %endif
</%def>

<%def name="hide_form(form)">
  %for field in form:
    <input type="hidden" name="${field.html_name | n }" value="${extract_field_data(field)}"/>
  %endfor
</%def>

<%def name="render_field(field, attrs=None)">
  ${field.as_widget(attrs=attrs) | n}
</%def>

<%def name="column_table(formset)">
  <%
    seq = 0
    name_attr = { "class": "export-column-name" }
    hive_attr = { "class": "export-hive-type", "type": "hidden" }
    db_attr   = { "class": "export-db-type" }
  %>
  % for form in formset.forms:
    <% seq += 1 %>
    <tr>
      <td class="export-column-no">${seq}</td>
      <td>${render_field(form["name"], name_attr)}</td>
      <td>${extract_field_data(form["hive_type"]) | n}${render_field(form["hive_type"], hive_attr)}</td>
      <td>${render_field(form["db_type"], db_attr)}</td>
    </tr>
  %endfor
</%def>

<%def name="overtext_input(field, attrs={}, dt_class='bw-input-label', dd_class='bw-input-field')">
  <%
    def append(attrs, name, value):
      if name not in attrs:
        attrs[name] = value
      elif attrs[name].find(value) == -1:
        attrs[name] += " " + value

    fld_attrs = attrs.copy()
    append(fld_attrs, "data-filters", "OverText")
    if len(field.errors):
      append(fld_attrs, "class", "validation-failed")

    if 'alt' not in fld_attrs:
      fld_attrs['alt'] = field.label
  %>
  <dt class="${dt_class}">${field.label_tag() | n}</dt>
  <dd class="${dd_class}">
    ${render_field(field, fld_attrs)}
  </dd>
</%def>

<%def name="table_name(table)">
  <span class="export-table-name">${unicode(table["name"]) | n}</span> on <span class="export-table-name">${unicode(table["db"]) | n}</span>
</%def>

<%def name="result_size(size)">
  ${human_size(size) | n }
</%def>

<%def name="step_list(wizard)">
  <ul class="nav nav-pills">
      % for idx in range(wizard.total_step_count):
        % if idx == wizard.step_index():
          <li class="active"><a id=${"step%s" % (idx+1,)} class="step" href="#">${ "Step %s: " % (idx+1,) + wizard.step().title}</a></li>
        % elif idx > wizard.done_step_index() + 1:
          <li><a class="step" herf="#">${"Step %s: " % (idx+1,) + wizard.step(idx).title}</a></li>
        % else:
          <li>${step("Step %s: " % (idx+1,) + wizard.step(idx).title, wizard.step_index(), idx)}</li>
        % endif
      % endfor
  </ul>
</%def>

<%def name="open_container(id)">
  <div class="container-fluid">
    <h1>${ _('Export to Database') }</h1>
    <div class="row-fluid">
      <div class="span3">
      <div class="well sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${_('Downloads')}</li>
          <li><a target="_blank" href="${url(app_name + ':download', id=id, format='csv')}">${_('Download as CSV')}</a></li>
          <li><a target="_blank" href="${url(app_name + ':download', id=id, format='xls')}">${_('Download as XLS')}</a></li>
          <li class="nav-header"></li>
          <li><a href="${url(app_name + ':watch_query', id=id, download_format=None)}">${_('Back to Results')}</a></li>
        </ul>
      </div>
    </div>
    <div class="span9">
</%def>

<%def name="close_container()">
  </div></div></div>
</%def>
