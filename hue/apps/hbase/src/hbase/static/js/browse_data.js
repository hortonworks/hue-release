$(document).ready(function (){

function Version(data){
    this.timestamp = ko.observable(data.timestamp);
    this.prevValue = ko.observable(data.prevValue);
}

function Column(data){
    this.columnName = ko.observable(data.columnName);
    this.value = ko.observable(data.value);
    this.versions = ko.observableArray(data.versions);
    
    this.editValue = function (){} //TODO
    this.dropCell = function(){} //TODO

    this.getVersions = function() {
        //TODO for cell
        // $.ajax("/hbase/table/versions/json/" + self.tableName + "/" + row.row() + "/" + row.column() , 
        //        {
        //            dataType: "JSON",
        //            success: function(resp) {
        //                console.log(resp.length);
        //                if (resp.length == 1) $.jHueNotify.info("There are no previous versions for this row");
        //                else {
        //                    for (var i = 1; i < resp.length; i++) {
        //                        console.log(resp[i]);
        //                        row.versions.push(new Version({prevValue: resp[i][0], timestamp: resp[i][1]}));
        //                    }
        //                }
        //            },
            
        //        });
    }


}
    
function ColumnFamily(data){
    this.cfName = ko.observable(data.cfName);
    this.columns = ko.observableArray(data.columns);

}

function Row(data)
{
    this.row = ko.observable(data.row);
    this.selected = ko.observable(data.selected);
    this.columnFamilies = ko.observableArray(data.columFamilies);
    
    this.dropRow = function(){
        
    }

}

function dataViewModel(){
    var self = this;
    self.tableName = $("#table_name").val();
    self.rows = ko.observableArray([]);
    self.column_families = ko.observableArray([]);
    self.nextPageRow = ko.observable();
    self.prevPageRow = ko.observable();

    self.cfValue = ko.observable().extend({ required: true });
    self.rowKeyValue = ko.observable().extend({ required: true });
    self.columnValue = ko.observable().extend({ required: true });
    self.valueVal = ko.observable().extend({ required: true });
    
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


    self.addRowModal = function (){
        $("#add_row").modal('show');
    }

    self.addRow = function(){
        var fqcn = self.cfValue() + ":" + self.columnValue();
        var data = {
            "row": self.rowKeyValue(),
            "column": fqcn, 
            "value": self.valueVal(),
            
        };
        
        $.post("/hbase/table/data/add/" + self.tableName, {"data": ko.toJSON(data)}, function(result){
            if(result["status"] == "done")
                window.location.reload(true); // TODO: make something dynamic.
        }, "JSON");
    }

    $.getJSON("/hbase/table/data/json/" + self.tableName , function(allData) {
        $(allData["cfs"]).map(function(i, cf){self.column_families.push(cf)});
        var data = allData["data"];
        $(data).map(function(i, el){
            var row = new Row({row: el[0]});
            for (var cf in el[1]){
                var columnFamily = new ColumnFamily({cfName: cf});
                $(el[1][cf]).map(function(i, data){
                    for(var c in data){
                        console.log("Adding column...");
                        //console.log({columnName: c, value: data[c]});
                        columnFamily.columns.push(new Column({columnName: c, value: data[c]}))
                    }
                });
                row.columnFamilies.push(columnFamily);
            }
            self.rows.push(row);
        });
    });  
    

}
    
ko.applyBindings(new dataViewModel());

});
