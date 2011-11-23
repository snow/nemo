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

/**
 * stream
 * ----------
 */
(function($){
    var j_stream,
        vote_buffer = {};
    
    function parse_vote_count(str){
        var matches = str.match(/\d+/);
        if(matches){
            return parseInt(matches[0]);
        } else {
            return 0;
        }
    }
    
    function vote(j_link){
        var vote_count = parse_vote_count(j_link.text()),
            sid = j_link.closest('.stream_li').attr('sid'),
            API_URI = '/vote/'+sid+'/';
            
        if(j_link.hasClass('ay')){
            if(3 > vote_count){
                vote_count += 1;
                j_link.text('+'+vote_count);
            } else {
                vote_count = 0;
                j_link.text('ay');
            }
        } else {
            vote_count = -vote_count;
            if(-3 < vote_count){
                vote_count -= 1;
                j_link.text(vote_count);
            } else {
                vote_count = 0;
                j_link.text('ng');
            }
        }
        
        try{
            clearTimeout(vote_buffer[sid]);
        } catch(e) {}
        
        vote_buffer[sid] = setTimeout(function(){
            n.ajax(API_URI, {
                data: {'count': vote_count},
                success: function(data){
                    if(!data.done){
                        alert('U dont have only '+data.has+' votes left');
                    }
                    location.reload();
                },
                dataType: 'json'
            });
        }, 500);
    }
    
    function edit(j_content){
        var j_li = j_content.closest('.stream_li'),
            j_form = j_li.find('.wishform');
            
        j_content.hide();
        j_form.show().find('textarea').focus();
    }
    
    function cancel_form(j_link){
        var j_form = j_link.closest('form'),
            j_li = j_form.closest('.stream_li'),
            j_content = j_li.find('.content'),
            j_status = j_li.find('.status');
            
        j_content.show();
        j_status.show();
        j_form.hide();
    }
    
    function response(j_link){
        var j_li = j_link.closest('.stream_li'),
            j_form = j_li.find('.responseform'),
            j_response = j_li.find('.status');
            
        j_form.show();
        j_response.hide();
    }
    
    function update_status(j_link){
        var j_form = j_link.closest('form'),
            j_select = j_form.find('[name=status]');
        
        j_form.find('.status_select .on').removeClass('on');
        j_link.addClass('on');    
        j_select.find('option:contains('+j_link.text()+')').attr('selected', 
                                                                 'selected');
    }
    
    n.stream = {};
    n.stream.init = function(){
        j_stream = $('.stream');
        
        j_stream.delegate('.ay:not(.signin), .negative:not(.signin)', 'click', 
                function(e){
                    e.preventDefault();
                    vote($(this));
                }).
            delegate('.content.editable', 'click', function(e){
                e.preventDefault();
                edit($(this));
            }).
            delegate('.cancel', 'click', function(e){
                e.preventDefault();
                cancel_form($(this));
            }).
            delegate('.oprts .response', 'click', function(e){
                e.preventDefault();
                response($(this));
            }).
            delegate('.status_select a', 'click', function(e){
                e.preventDefault();
                update_status($(this));
            });
        
        j_stream.load('/list/');
    }    
})(jQuery);