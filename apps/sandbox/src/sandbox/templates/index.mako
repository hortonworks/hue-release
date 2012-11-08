<%!from desktop.views import commonheader, commonfooter %>
<%namespace name="shared" file="shared_components.mako" />

${commonheader("Sandbox", "Sandbox", user, "100px")}
${shared.menubar(section='configuration')}

## Use double hashes for a mako template comment
## Main body

<div class="container-fluid">
  ##<h2>Sandbox app is successfully setup!</h2>
  ##<p>It's now ${date}.</p>
</div>
${commonfooter(messages)}
