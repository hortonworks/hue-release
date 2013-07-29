$(document).ready(function(){

    function TableView(){
        var self = this;
        this.isEnabled = parseInt($("#table_enabled").val());

        this.tableName = $("#table_name").val();

        this.dropTableConfirm = function(){
            $("#modal-from-dom").modal('show');            
        }
        
        this.dropTable = function(){
            $.ajax({url: "/hbase/table/drop/" + this.tableName, 
                    async: false,
                    type: "DELETE", 
                    success: function(result){
                        window.location.href="/hbase";
                    }});
            
            
        }
        
        this.disableTable = function(){

        }

        this.enableTable = function(){

        }

        this.compactTable = function(){
            
        }

        this.compactTableModal = function(){
            $("#compactionModal").modal('show');
        }
        

    }

    ko.applyBindings(new TableView());

});
