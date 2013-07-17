$(document).ready(function (){

function Version(data){
    this.timestamp = ko.observable(data.timestamp);
    this.prevValue = ko.observable(data.prevValue);
}

function Row(data)
{
    this.row = ko.observable(data.row);
    this.selected = ko.observable(data.selected);
    this.column = ko.observable(data.column);
    this.value = ko.observable(data.value);
    this.versions = ko.observableArray(data.versions);
}

function dataViewModel(){
    var self = this;
    self.tableName = $("#table_name").val();
    self.rows = ko.observableArray([]);
    self.column_families = ko.observableArray([]);
    self.nextPageRow = ko.observable();
    self.prevPageRow = ko.observable();
    
    self.selectAlldata = function(data, event)
    {
        ko.utils.arrayForEach(self.rows(), function(item){
            if (event.target.checked)
                item.selected(true);
            else
                item.selected(false);
        });
        return true; 
    }
    
    self.slectedRows = function() {
        return ko.utils.arrayFilter(self.rows(), function(row) { return row.selected() });
    }

    self.getVersions = function() {
        var row = self.slectedRows()[0];
        $.ajax("/hbase/table/versions/json/" + self.tableName + "/" + row.row() + "/" + row.column() , 
               {
                   dataType: "JSON",
                   success: function(resp) {
                       console.log(resp.length);
                       if (resp.length == 1) $.jHueNotify.info("There are no previous versions for this row");
                       else {
                           for (var i = 1; i < resp.length; i++) {
                               console.log(resp[i]);
                               row.versions.push(new Version({prevValue: resp[i][0], timestamp: resp[i][1]}));
                           }
                       }
                   },
            
               });
    }

    $.getJSON("/hbase/table/data/json/" + self.tableName , function(allData) {
        self.column_families = allData["cfs"];
        var data = allData["data"];
        for (var i = 0 ; i < data.length; i++){
            var r = new Row({row: data[i][0], column: data[i][1], value: data[i][2]});
            self.rows.push(r);
        }
    });  
    

}
    
ko.applyBindings(new dataViewModel());

});
