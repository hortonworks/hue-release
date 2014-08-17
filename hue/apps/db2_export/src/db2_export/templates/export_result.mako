<%!
from desktop.views import commonheader, commonfooter
from db2_export.models import ExportState
from django.utils.translation import ugettext as _
%>
<%namespace name="layout" file="layout.mako" />
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="export" file="export_components.mako" />


${commonheader(_("Export to Database"), app_name, user, "100px") | n,unicode }
${layout.menubar(section='tables')}
<%
  if req.new_table:
    show_create_table = True
    create_op = "Created"
  elif req.recreation:
    show_create_table = True
    create_op = "Dropped, then recreated"
  else:
    show_create_table = False

  if req.existing_table and not req.recreation:
    if req.operation == "insert":
      load_op = "Appending"
    else:
      load_op = "Replacing"
  else:
    load_op = "Loading"
%>
${ export.open_container(query_id) }
  <div class="span9">
    ${export.step_list(wizard)}
    <ul class="nav nav-tabs">
      <li class="active"><a href="#results" data-toggle="tab">${_("Result")}</a></li>
      <li><a href="#log" data-toggle="tab">${_("Log")}</a></li>
    </ul>
    <div class="tab-content">
      <div class="active tab-pane" id="results">
        <div class="control-group">
          % if show_create_table:
            <div class="export-step-table controls">
              ${create_op |n } ${export.table_name(table)} successfully.
            </div>
          % endif
          <div class="export-step-waiting controls">
            Waiting ...
          </div>
          <div class="export-step-running controls">
            <div>${unicode(load_op) | n} data into ${export.table_name(table)}</div>
            <table class="export-metrics table table-striped">
              <tr>
                <td class="export-metric-label"> Total size: </td>
                <td class="export-total-size">
                  % if state.size > 0:
                    ${export.result_size(state.size) | n}
                  % else:
                    &lt; ${export.result_size(limit) | n}
                  % endif
                </td>
              </tr>
              <tr>
                <td class="export-metric-label"> Finished size:</td>
                <td class="export-finished-size"> </td>
              </tr>
              <tr>
                <td class="export-metric-label"> Finished rows:</td>
                <td class="export-finished-rows"> </td>
              </tr>
            </table>
          </div>
        </div>
        <div class="export-step-summary">
          <div class="export-step-failed">Failed to send data to ${export.table_name(table)}</div>
          <div class="export-step-exceeded">Query result exceeds the limit ${export.result_size(limit)}. </div>
          <div class="export-step-success">Exported successfully.</div>
          <div class="export-step-partial">Not all data is loaded into ${export.table_name(table)} </div>
          <div class="export-metric-comparison">
            <table class="export-metrics-layout table table-striped">
              <tr>
                <td>
                  <table class="export-metrics table">
                    <caption>Query Result</caption>
                    <tr>
                      <td class="export-metric-label">Result size</td>
                      <td class="export-finished-size metric"></td>
                    </tr>
                    <tr>
                      <td class="export-metric-label">Result rows:</td>
                      <td class="export-finished-rows metric"></td>
                    </tr>
                  </table>
                </td>
                <td style="width:4em;">&nbsp;</td>
                <td>
                  <table class="export-metrics table table-bordered">
                    <caption>DB2 Load:</caption>
                    <tr>
                      <td class="export-metric-label"># of rows read</td>
                      <td class="export-db-read metric"></td>
                    </tr>
                    <tr>
                      <td class="export-metric-label"># of rows skipped</td>
                      <td class="export-db-skipped metric"></td>
                    </tr>
                    <tr>
                      <td class="export-metric-label"># of rows inserted</td>
                      <td class="export-db-inserted metric"></td>
                    </tr>
                    <tr>
                      <td class="export-metric-label"># of rows rejected</td>
                      <td class="export-db-rejected metric"></td>
                    </tr>
                    <tr>
                      <td class="export-metric-label"># of rows updated</td>
                      <td class="export-db-updated metric"></td>
                    </tr>
                    <tr>
                      <td class="export-metric-label"># of rows commited</td>
                      <td class="export-db-committed metric"></td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </div>
        </div>
        ${export.export_buttons(query_id)}
      </div>
      <div class="tab-pane" id="log">
      </div>
    </div>
  </div>
${export.close_container()}

<style type="text/css">
.export-step-table {
    font-size: 14px;
    padding-left: 20px;
    background: url(/static/art/task_status/succeeded.png) no-repeat;
}
.export-step-waiting {
    font-size: 14px;
    padding-left: 20px;
    background: url(/static/art/spinner.gif) no-repeat;
    display: none;
}
.export-step-running {
    font-size: 14px;
    padding-left: 20px;
    background: url(/static/art/spinner.gif) no-repeat;
    display: none;
}
.export-step-failed {
    font-size: 14px;
    padding-left: 20px;
    background: url(/static/art/led-icons/cross.png) no-repeat;
    display: none;
}
.export-step-success {
    font-size: 14px;
    padding-left: 20px;
    background: url(/static/art/task_status/succeeded.png) no-repeat;
    display: none;
}
.export-step-exceeded {
    font-size: 14px;
    padding-left: 20px;
    background: url(/static/art/led-icons/stop.png) no-repeat;
    display: none;
}
.export-step-partial {
    font-size: 14px;
    padding-left: 20px;
    background: url(/static/art/led-icons/exclamation_octagon_fram.png) no-repeat;
    display: none;
}
.export-step-summary {
    display: none;
}
.export-metric-comparison {
    padding-left: 20px;
}
</style>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function(){
    var widgets = {};
    $.each(["waiting", "running", "summary", "failed", "exceeded", "partial", "success"], function() {
      widgets[this] = $(".export-step-" + this);
    });
    var metrics = {};
    $.each(["size", "rows"], function(){
      metrics[this] = $(".export-finished-" + this);
    });
    var loadMetricNames = ["read", "skipped", "inserted", "rejected", "updated", "committed"];
    $.each(loadMetricNames, function() {
      metrics[this] = $(".export-db-" + this);
    });
    var prvWidget = widgets["waiting"];
    prvWidget.show();

    var timer;
    var stateRequest = function() {
      $.getJSON("${ url(app_name + ':export_state', id=state.id) }", function(state){
        widget = widgets[state.state];
        if(widget && widget != prvWidget){
          prvWidget.hide();
          widget.show();
          prvWidget = widget;
        }
        if(state.state == "submitted"){
          // do nothing
        } else if(state.state == "running") {
          metrics["size"].html(state.finished_size);
          metrics["rows"].html(state.finished_rows);
        } else {
          if(state.stdout) {
            // Stop request
            $("#log").html("<pre>"+state.stdout+"</pre>")
            clearTimeout(timer);
          }
          metrics["size"].html(state.finished_size);
          metrics["rows"].html(state.finished_rows);
          $.each(loadMetricNames, function() {
            metrics[this].html(state[this]);
          });
          widgets["summary"].show();
        }
      });
      timer = setTimeout(stateRequest, 2000);
    }; // end of function stateRequest
    timer = setTimeout(stateRequest, 2000);
  });
</script>

${commonfooter(messages) | n,unicode } 
