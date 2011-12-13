/**
 * namespace and basic
 * --------------------
 */
(function($){
    window.rcp = {
        j_doc: $(document)
    }
    
    /*var IS_DOC_READY = false;
    rcp.is_ready = function(){
        return IS_DOC_READY;
    }
    
    rcp.j_doc.one('ready', function(evt){
        IS_DOC_READY = true;
    });
    
    var DEBUG = false;
    rcp.debug = function(){
        return DEBUG;
    };
    
    rcp.set_debug = function(debug_){
        DEBUG = debug_;
    };*/
})(jQuery);

/**
 * logging
 * ---------
 */
(function($){
    rcp.l = function(){
        if(!(console && console.log)){return;}
        
        for(var i=0; i < arguments.length; i++){
            if('function' === typeof arguments[i]){
                console.log(arguments[i]());
            } else {
                console.log(arguments[i]);
            }
        }
    };
})(jQuery);

/**
 * preload image
 * --------------------
 */
(function($){
    var j_ctn = $('<div id="rcp-preimg" />'),
        j_img_tpl = $('<img src="" alt="" />');
        
    rcp.j_doc.one('ready', function(evt){
        // there are no 'body' element when this script load in header
        j_ctn.appendTo($('body'));
    });
    
    rcp.preimg = function(src){
        j_ctn.find('[src="'+src+'"]').length || 
        j_ctn.append(j_img_tpl.clone().attr('src', src));
    }
})(jQuery);