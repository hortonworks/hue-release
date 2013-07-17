<%!
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

${ commonheader(_('Hbase'), 'hbase', user) | n,unicode }
<%namespace name="actionbar" file="actionbar.mako" />

<div class="container-fluid" id="tables">
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Actions')}</li>
                    <li><a href="/hbase/table/drop/${table.name}">${_('Drop table')}</a></li>
                    <li><a href="/hbase/table/browse/${table.name}">${_('Brows data')}</a></li>
                </ul>
            </div>
        </div>
        <div class="span9">
          <div class="span4">
          <table class="table-hover table-condensed table-bordered">
            <caption>Column Families</caption>
            <thead>
              <tr>
                <th>Name</th>
                <th>Options</th>
              </tr>
            </thead>
            <tbody>
              % for cf, options in table.families().iteritems():
              <tr>
                <td>${cf}</td>
                <td>
                  <ul>
                    % for k,v in options.iteritems(): 
                    <li>${k}: ${v}</li>
                    % endfor
                  </ul>
                </td>
              </tr>
              % endfor
            </tbody>
          </table>
          </div>
          <div class="span4">
            <table class="table-hover table-condensed table-bordered">
              <caption>Regions</caption>
              <tbody>
                % for region in table.regions():
                <tr>
                  <td>
                    <ul>
                      % for k,v in region.iteritems():
                      <li>${k}: ${v}</li>
                      % endfor
                    </ul>
                  </td>
                </tr>
                % endfor
            </table>
          </div>
        </div>
    </div>
</div>


${ commonfooter(messages) | n,unicode }
