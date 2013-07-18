$(document).ready(function (){
    
    function Table(data){
        this.name = ko.observable(data.name);
        this.enabled = ko.observable(data.enabled);
        this.browseDataUrl = ko.observable(data.browseDataUrl);
        this.url = ko.observable(data.url);
        this.selected = ko.observable(data.selected);
        
        this.disabledName = function(){
            if (!this.enabled()) return this.name() + '&nbsp;<span class="badge">disabled</span>' ;
            else return this.name();
        }
    }

    function TableViewModel(){
        var self = this;
        self.tables = ko.observableArray([]);
        
        
        $.getJSON("/hbase/tables/list/json"  , function(data) {
            for (var row in data){
                self.tables.push(new Table({name: row, enabled: data[row], browseDataUrl: "/hbase/table/browse/" + row, url: "/hbase/table/view/" + row, selected: false}))
            }
            self.tables.sort(function(t1, t2) {
                return t1.name().localeCompare(t2.name());
            });
        });

        self.enabledFilter = function(){
            return ko.utils.arrayFilter(self.tables(), function(table) {
                return (table.selected() && table.enabled()); });
        };

        self.disabledFilter = function(){
            return ko.utils.arrayFilter(self.tables(), function(table) {
                return (table.selected() && !table.enabled()); });

        };
        
        self.selectedFilter = function(){
            return ko.utils.arrayFilter(self.tables(), function(table) {
                return table.selected(); });
        }

        self.askCompactionType = function() {
            $("#compactionModal").modal();
        }

        self.compact = function() {
            var tables = self.selectedFilter();
            var mode = $("input[name=compactionType]").val() == "major" ? "compactionType=true" : "";
            for (var i = 0; i < tables.length; i++){
                var table = tables[i];
                console.log(table.name());
                $.ajax({url: "/hbase/table/compact/" + table.name(), 
                        async: false,
                        data: mode,
                        type: "POST", 
                        success: function(result){
                            table.selected(false);
                    }});
            }
            $("#compactionModal").modal('hide');
                
        }

        
        
        self.disableTables = function(){
            $("#op_progres").show();
            var tables = self.enabledFilter();
            for (var i = 0; i < tables.length; i++)
                {
                    var table = tables[i];
                    $.ajax({url: "/hbase/table/disable/" + table.name(), 
                            async: false,
                            type: "POST", success: function(result){
                       table.selected(false);
                        table.enabled(false);
                       $(".bar").css("width", table.length / i + "%");
                    }});
                }
            //$("#op_progres").hide();
        };
        

        self.enableTables = function(){
            var tables = self.selectedFilter();
            ko.utils.arrayForEach(tables, function(table) {
                if (table.enabled()) {
                    $("#alertText").text("Table " + table.name() + "already enabled.");
                    $("#tableAlert").modal();
                    table.selected(false);
                }
            });

            $(tables).map(function (i, table){
                    $.ajax({url: "/hbase/table/enable/" + table.name(), 
                            async: false,
                            type: "POST", success: function(result){
                       table.selected(false);
                       table.enabled(true);
                       console.log(table.name());

                    }});
                });
        };

        self.confirmDelete = function () {
            var tables = self.selectedFilter();
            $("#deleteTableList").empty()
            $(tables).map(function (i, table) {
                console.log(table);
                $("#deleteTableList").append("<li>" + table.name() + "</li>");
            });
            $('#modal-from-dom').modal();
        }
        
        self.deleteTables = function(){
            var tables = self.selectedFilter();
            $(tables).map(function (i, table) {
                $.ajax({url: "/hbase/table/drop/" + table.name(), 
                        async: false,
                        type: "DELETE", 
                        success: function(result){
                            table.selected(false);
                        }});
            });
            $('#modal-from-dom').modal('hide');
        }


    }

ko.applyBindings(new TableViewModel());
    
});
