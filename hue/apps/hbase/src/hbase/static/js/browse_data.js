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
    this.editModeValue = '';

    this.rowID = function(){
        return self.rowKey + '_' + this.parent().cfName() + '_' + this.columnName();
    }

    this.editCell = function (data, event){
        var valbox = $('#p_'+self.rowID());

        var showMode =  function (){
          $(event.target).prev().show();
          $(event.target).hide();
          
          valbox.next().css("height", '38').hide();
          valbox.show();
          self.editMode = false;
          self.value(self.editValue());
        }
        
        if (!self.editMode){
            $(event.target).next().show();
            $(event.target).hide();
            
            console.log(self.rowID());
            this.editModeValue = self.editValue();

            valbox.next().show();
            scrollHeight = valbox.next()[0].scrollHeight;
            if (scrollHeight)
              valbox.next().css("height", scrollHeight + 5);

            valbox.hide();
            self.editMode = true;
        } else {
            if (this.editModeValue != self.editValue()){
              $.ajax({
                  url: '/hbase/table/data/edit/' + self.tableName,
                  dataType: "json",
                  type: "POST",
                  data: "row=" + self.rowKey + "&col=" + self.fqcn + "&val=" + self.editValue(),
                  success: function(result){
                      showMode();
                  }
              });
            } else {
              showMode();  
            }
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
                //
                if (self.parent().columns().length == 1){
                    if (self.parent().parent().columnFamilies().length == 1) {                        
                        self.parent().parent().removeMyself();
                    }
                    else{
                        self.parent().parent().columnFamilies(self.parent().parent().columnFamilies.remove(self.parent()));
                    }
                }
                else{
                    self.parent().columns(self.parent().columns.remove(self));
                }

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
    
    this.parent = ko.observable(data.parent);

    this.removeMyself = function(){
        self.parent().rows.remove(self);
    }
    
    this.dropRow = function(){
        if (!confirm("Are you sure you want to delete row?")) return; //TODO Change confirm to modal
        $.ajax({
            url: "/hbase/table/data/delete/" + this.tableName,
            data: "row=" + self.row(),
            type: "POST",
            dataType: "json",
            success: self.removeMyself,
        });
    }

    
    

}

function dataViewModel(){
    var self = this;
    self.tableName = $("#table_name").val();
    self.rows = ko.observableArray([]);
    self.column_families = ko.observableArray([]);
    self.nextPageRow = ko.observable(); 
    self.prevPageRow = ko.observable();
    
    
    self.rowsPerPage = ko.observable();
    self.rowsPerPage.subscribe(function(newVal){self.getJSONData()});
    self.veryFirstRow = null;

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
            var row =  ko.utils.arrayFilter(self.rows(), function(r){ return r.row() == self.rowKeyValue();});
            console.log(row);
            if (row.length) { //If there is row
                row = row[0];
                var cf = ko.utils.arrayFilter(row.columnFamilies(), function(cf) {return cf.cfName() == self.cfValue();});
                console.log(cf);
                if (!cf.length) //There is no Column Family
                {
                    console.log("DDD");
                    var newColumFamily = new ColumnFamily({parent: row, cfName: self.cfValue()});
                    var col = new Column({columnName: self.columnValue(), value: self.valueVal(), parent: newColumFamily});
                    newColumFamily.columns.push(col);
                    row.columnFamilies.push(newColumFamily);
                }
                else{ //There is column family. Let's search for column
                    cf = cf[0];
                    var col = ko.utils.arrayFilter(cf.columns(), function(c) {return c.columnName() == self.columnValue();});
                    if (!col.length) // There is no column. 
                    {
                        col = new Column({parent: cf, value: self.valueVal(), columnName: self.columnValue()});
                        cf.columns.push(col);
                    }
                    else // Update value
                    {
                        col = col[0];
                        col.value(self.valueVal());
                    }
                }
            }
            else{ //There is no row. Simply add it
                var newRow = new Row({parent: self, row: self.rowKeyValue()});
                var cf = new ColumnFamily({parent: newRow, cfName: self.cfValue()});
                var col = new Column({parent: cf, columnName: self.columnValue(), value: self.valueVal()});
                cf.columns.push(col);
                newRow.columnFamilies([cf]);
                self.rows.push(newRow);
            }
            $("#add_row").modal('hide');
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
            var row = new Row({row: el[0], parent: self});            
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
        

        if (data.length == (parseInt(self.rowsPerPage()) + 1)) {
            self.nextPageRow(self.rows.pop());
        }
        else{
            self.nextPageRow(null);
        }
        

        if ((self.veryFirstRow != null) && (self.rows()[0].row() == self.veryFirstRow.row())) // If it's first page
            self.prevPageRow(false);
        
        if(self.veryFirstRow === null)
            self.veryFirstRow = self.rows()[0];

    }

    this.getJSONData = function(nextRow){
        params = {};
        params.rows = parseInt(self.rowsPerPage())+1;
        if (self.queryFilter())
            params.query = self.queryFilter();
        if (nextRow && self.nextPageRow())
            params.row_start = self.nextPageRow().row()

        $.getJSON("/hbase/table/data/json/" + self.tableName, $.param(params), self.addData);  
    };

    this.getJSONData();

    self.getNextData = function(){
        self.prevPageRow(self.rows()[0]);
        self.getJSONData(true);
    }

    self.getPrevData = function()
    {
        self.nextPageRow(self.prevPageRow());
        self.getJSONData(true);
    }

}
    
ko.applyBindings(new dataViewModel());

});
