$(document).ready(function (){

function Version(data){
    this.timestamp = ko.observable(data.timestamp);
    this.prevValue = ko.observable(data.prevValue);
}

function Column(data){
    var self = this;
    this.columnName = ko.observable(data.columnName);
    this.value = ko.observable(data.value);
    this.editValue = ko.observable(this.value());
    this.versions = ko.observableArray([]);
    
    this.parent = ko.observable(data.parent);
    
    this.rowKey = this.parent().parent().row();
    this.fqcn = this.parent().cfName() + ':' + this.columnName();
    
    this.editMode = false;

    this.rowID = function(){
        return self.rowKey + '_' + this.parent().cfName() + '_' + this.columnName();
    }

    this.editCell = function (data, event){
        if (!self.editMode){
            $(event.target).next().show();
            $(event.target).hide();
            
            console.log(self.rowID());
            
            $('#p_'+self.rowID()).next().show()
            $('#p_'+self.rowID()).hide();
            self.editMode = true;
        }
        else {
            $.ajax({
                url: '/hbase/table/data/edit/' + self.tableName,
                dataType: "json",
                type: "POST",
                data: "row=" + self.rowKey + "&col=" + self.fqcn + "&val=" + self.editValue(),
                success: function(result){
                    $(event.target).prev().show();
                    $(event.target).hide();
                    
                    $('#p_'+self.rowID()).next().hide()
                    $('#p_'+self.rowID()).show();
                    self.editMode = false;
                    self.value(self.editValue());
                }
            });
            
        }
    } 


    this.dropCell = function(){
        if (!confirm("Are you sure you want to delete cell?")) return; //TODO change confirm to modal
        $.ajax({
            url: "/hbase/table/data/delete/" + this.tableName,
            data: "row="+ self.rowKey + "&col=" + self.fqcn,
            type: "POST",
            dataType: "json",
            success: function(result){
                if (result["status"] == "done")
                    window.location.reload(true);
                // TODO:
                // self.parent().columns.remove(self);
                // if self.parent().columns().lenght == 0 - If there are no columns in CF
                // && self.parent().parent().columnFamilies().lenght == 1 And only one CF left
                // Remove row!                
            }
        });
            
    } 

    this.tableName = $("#table_name").val();

    this.getVersions = function(data, event) {
        self.versions([]);
        $.ajax("/hbase/table/versions/json/" + this.tableName, 
               {
                   dataType: "JSON",
                   data: "col=" + self.fqcn + "&row=" + self.rowKey,
                   success: function(resp) {
                       if (resp.length == 1) $.jHueNotify.info("There are no previous versions for this cell");
                       else {
                           for (var i = 1; i < resp.length; i++) {
                               self.versions.push(new Version({prevValue: resp[i][0], timestamp: resp[i][1]}));
                           }
                       }
                   },
               });
    }
    

}
    
function ColumnFamily(data){
    this.cfName = ko.observable(data.cfName);
    this.columns = ko.observableArray(data.columns);
    this.parent = ko.observable(data.parent);
}

function Row(data)
{
    var self = this;
    this.row = ko.observable(data.row);
    this.selected = ko.observable(data.selected);
    this.columnFamilies = ko.observableArray(data.columFamilies);
    this.tableName = $("#table_name").val();
    
    
    this.dropRow = function(){
        if (!confirm("Are you sure you want to delete row?")) return; //TODO Change confirm to modal
        $.ajax({
            url: "/hbase/table/data/delete/" + this.tableName,
            data: "row=" + self.row(),
            type: "POST",
            dataType: "json",
            success: function(result){
                if (result["status"] == "done")
                    window.location.reload(true);
                // TODO: 
                //delete self from Rows array;
            }
        });
    }

    
    

}

function dataViewModel(){
    var self = this;
    self.tableName = $("#table_name").val();
    self.rows = ko.observableArray([]);
    self.column_families = ko.observableArray([]);
    self.nextPageRow = ko.observable(); //TODO: make pagination
    self.prevPageRow = ko.observable();

    self.cfValue = ko.observable().extend({ required: true });
    self.rowKeyValue = ko.observable().extend({ required: true });
    self.columnValue = ko.observable().extend({ required: true });
    self.valueVal = ko.observable().extend({ required: true });
    
    self.queryFilter = ko.observable();
    
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
                window.location.reload(true); 
            // TODO: 
            //if self.rows.filter(self.rowKeyValue()) -If there is row with such key
            // Find this row-> search for column.
            //If column exists -> Update value for column
            // Else Update column for Row
            //else:
            //self.rows.push(new Row(data))
        }, "JSON");
    }

    self.addData = function(allData) {
        self.rows([]);
        self.column_families([]);
        $(allData["cfs"]).map(function(i, cf){self.column_families.push(cf)});
        var data = allData["data"];
        $(data).map(function(i, el){
            var row = new Row({row: el[0]});
            for (var cf in el[1]){
                var columnFamily = new ColumnFamily({cfName: cf, parent: row});
                $(el[1][cf]).map(function(i, data){
                    for(var c in data){
                        columnFamily.columns.push(new Column({columnName: c, value: data[c], parent: columnFamily}))
                    }
                });
                row.columnFamilies.push(columnFamily);
            }
            self.rows.push(row);
        });
    }

    $.getJSON("/hbase/table/data/json/" + self.tableName, self.addData);  

    self.filterData = function(data, event) {
        $.getJSON("/hbase/table/data/json/" + self.tableName, "query="+ self.queryFilter(), self.addData);  
    }    

}
    
ko.applyBindings(new dataViewModel());

});
