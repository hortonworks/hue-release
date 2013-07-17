$(document).ready(function(){
function ColumnFamily(data) {
   this.name = ko.observable(data.name);
   this.max_versions = ko.observable(data.max_versions);
   this.compression = ko.observable(data.compression_type);
   this.in_memory = ko.observable(data.in_memory);
   this.time_to_live = ko.observable(data.ttl);
   this.bloom_filter_nb_hashes = ko.observable(data.bloomFilterNumHashes);
   this.block_cache_enabled = ko.observable(data.block_cache_enabled)
   this.toRemove = ko.observable(data.toRemove)

   this.options = ko.computed(function() {
    var options = "<ul>";

    if (this.max_versions()) options += "<li>max versions: " +
    this.max_versions() + "</li>";

    if (this.compression()) options += "<li>compression type: " +
    this.compression() + "</li>";
    
    if (this.in_memory()) options += "<li>in memory: true</li>";

    
    if (this.time_to_live()) options += "<li>Time to live: " + this.time_to_live() + 
    "</li>";
    
    if (this.bloom_filter_nb_hashes()) options += "<li>Bloom filter number of hashes: " + this.bloom_filter_nb_hashes() +"</li>";

    if (this.block_cache_enabled()) options += "<li>Block cache enabled: true</li>";    

    return options;
   }, this);
   

}

ko.numericObservable = function(initialValue) {
    var _actual = ko.observable(initialValue);

    var result = ko.dependentObservable({
        read: function() {
            return _actual();
        },
        write: function(newValue) {
            var parsedValue = parseFloat(newValue);
            _actual(isNaN(parsedValue) ? newValue : parsedValue);
        }
    });

    return result;
};

function CFViewModel(){
   var self = this;
   
   self.cf = ko.observableArray([]);

   self.cfNameText = ko.observable().extend({ required: true });
   self.maxVersionsValue = ko.numericObservable(3).extend({min: 1});
   self.compressionTypeValue = ko.observable();
   self.inMemoryValue = ko.observable();
   self.ttlValue = ko.numericObservable();
   self.bloomFilterNumHashesVal = ko.numericObservable();
   self.bloomFilterTypeValue = ko.observable();
   self.blockCacheValue = ko.observable();
   

   self.removeCF = function () {       
       self.cf.destroy(function(item) {return item.toRemove()});
   }


    self.selectAllCFs = function(data, event)
    {
        ko.utils.arrayForEach(self.cf(), function(item){
            if (event.target.checked)
                item.toRemove(true);
            else
                item.toRemove(false);
        });
        return true; //to trigger the browser default bahaviour
    }


   self.addCF = function() {
     self.cf.push(new ColumnFamily({
       name: this.cfNameText(),
       max_versions: this.maxVersionsValue(),
       compression_type: this.compressionTypeValue(),
       in_memory: this.inMemoryValue(),
       ttl: this.ttlValue(),
       bloomFilterNumHashes: this.bloomFilterNumHashesVal(),
       block_cache_enabled: this.blockCacheValue()             
     }));
       $("#cf_form")[0].reset();
       $("#cf_popup").modal('hide');
   }

   self.jsonData = function() {
       var copy = ko.toJS(self.cf());
       var result = {};
       $.each(copy, function(i, cf) {
           delete cf["options"];
           delete cf["toRemove"];
           var key = cf["name"];
           delete cf["name"];
           result[key] = cf;
       } );
       return ko.toJSON(result);
   }

}

ko.applyBindings(new CFViewModel());

});
