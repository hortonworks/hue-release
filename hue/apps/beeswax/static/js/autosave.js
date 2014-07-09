function autosave(){
  if(editor != undefined)
  {
      editor.save();
  }
  $(".query").val($("#queryField").val());
  $.post("/beeswax/autosave_design/", $("#advancedSettingsForm").serialize());
  return true;
}
editor.on('change',autosave);
