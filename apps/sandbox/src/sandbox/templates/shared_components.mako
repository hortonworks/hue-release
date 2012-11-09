
<%!
def is_selected(section, matcher):
  if section == matcher:
    return "active"
  else:
    return ""
%>

<%def name="menubar(section='configuration')">
  <div class="subnav subnav-fixed">
    <div class="container-fluid">
      <ul class="nav nav-pills">
        <li class="${is_selected(section, 'configuration')}"><a href="#">Configuration</a></li>
      </ul>
    </div>
  </div>
</%def>
