/**
 * namespace and basic
 * --------------------
 */
(function($){
    window.n = {}

    n.j_doc = $(document);
    
    n.ajax = function(url, params){
        params.type = 'POST';
        
        if('undefined' === typeof n.csrf){
            n.csrf = $('[name=csrfmiddlewaretoken]').val();
        }
        if('undefined' === typeof params.data){
            params.data = {}
        }        
        params.data.csrfmiddlewaretoken = n.csrf
        
        return $.ajax(url, params);
    }
})(jQuery);