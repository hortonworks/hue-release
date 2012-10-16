<%!
from pig.models import PigScript
pig_scripts = PigScript.objects.filter(saved=True).all()
%>

<%def name="my_scripts()">
<h2>My scripts</h2>
<ul class="nav nav-list">
  % for v in pig_scripts:
  <li>
    <p>
      <a href="${url('pig.views.delete', v.id)}">
        <img src="/pig/static/art/delete.gif" alt="Delete" height="12" width="12">
      </a>
      <a href="${url('pig.views.script_clone', v.id)}">
	<img src="/pig/static/art/clone.png" alt="Delete" height="14" width="14">
      </a>
      <a href="${url('pig.views.index', obj_id=v.id)}">
	% if v.title: 
	${v.title}
        % else:
        no title
        % endif
      </a>&nbsp;&nbsp;
    </p>
  </li>
  % endfor
</ul>
<a class="btn" href="${url('root_pig')}">New script</a>
</%def>
