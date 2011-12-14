/**
 * namespace and basic
 * --------------------
 */
(function($){
    window.rcp.django = {}
})(jQuery);

/**
 * csrf
 */
(function($){
    var csrftoken = '';
    rcp.django.get_csrftoken = function(){
        if('' === csrftoken){
            csrftoken = $.cookie('csrftoken');
        }
        return csrftoken;
    }
    
    rcp.django.is_method_safe = function(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/i.test(method));
    }
    
    rcp.j_doc.ajaxSend(function(evt, xhr, settings) {
        if (!rcp.django.is_method_safe(settings.type) &&
                !settings.crossDomain) {
            xhr.setRequestHeader('X-CSRFToken', rcp.django.get_csrftoken());
        }
    });
})(jQuery);