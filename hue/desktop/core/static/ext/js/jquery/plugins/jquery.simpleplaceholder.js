/* https://github.com/marcgg/Simple-Placeholder */
/******************************

Simple Placeholder

******************************/

(function($) {
	var jsval = this.jsval = $.fn.val;
	$.simplePlaceholder = {
		placeholder_class: null,

		hide_placeholder: function(){
			var $this = $(this);
			if(jsval.call($this) == $this.attr('placeholder')){
				$this.val("").removeClass($.simplePlaceholder.placeholder_class);
			}
		},

		show_placeholder: function(){
			var $this = $(this);
			if(jsval.call($this) == ""){
				$this.val($this.attr('placeholder')).addClass($.simplePlaceholder.placeholder_class);
			}
		},

		prevent_placeholder_submit: function(){
			$(this).find(".simple-placeholder").each(function(e){
				var $this = $(this);
				if(jsval.call($this) == $this.attr('placeholder')){
					$this.val('');
				}
			});
			return true;
		}
	};

	$.fn.simplePlaceholder = function(options) {
		// for IE
		if(document.createElement('input').placeholder == undefined){
			var config = {
				placeholder_class : 'placeholding'
			};

			if(options) $.extend(config, options);
			$.simplePlaceholder.placeholder_class = config.placeholder_class;

			// with all regards to IE overriding original val() function
			$.fn.val = function(value) {
				if (typeof value == 'undefined') {
					if ($(this).attr('placeholder') == jsval.call(this)){
						return "";
					}
					return jsval.call(this);
				}else {
					return jsval.call(this, value);
				}
			};

			this.each(function() {
				var $this = $(this);
				$this.focus($.simplePlaceholder.hide_placeholder);
				$this.blur($.simplePlaceholder.show_placeholder);
				if(jsval.call($this) == '') {
					$this.val($this.attr("placeholder"));
					$this.addClass($.simplePlaceholder.placeholder_class);
				}
				$this.addClass("simple-placeholder");
				$(this.form).submit($.simplePlaceholder.prevent_placeholder_submit);
			});
		}

		return this;
	};

})(jQuery);