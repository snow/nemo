/**
 * namespace and basic
 * --------------------
 */
(function($){
    window.nemo = {
        uri_root: ''
    }
})(jQuery);
/**
 * stream
 * ----------
 */
(function($){
    var j_stream,
        vote_buffer = {},
        
        OUT_OF_VOTE_MSG = 'You need {want} votes but only got {has} left';
    
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
            API_URI = nemo.uri_root+'vote/'+sid+'/';
            
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
            $.ajax(API_URI, {
                type: 'POST',
                data: {'count': vote_count},
                dataType: 'html',
                success: function(data){
                    j_link.closest('.stream_li').replaceWith(data);
                },
                error: function(xhr){
                    try {
                        resp = $.parseJSON(xhr.responseText);
                        //rcp.l(resp);
                        alert(OUT_OF_VOTE_MSG.replace('{want}', resp.want).
                                              replace('{has}', resp.has));
                    } catch(err) {
                        // TODO extractly what will happen here?
                    }
                },
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
    
    function hijax_form_submit(evt){
        evt.preventDefault();
        var j_form = $(evt.target);
        
        $.ajax(j_form.attr('action'), {
            type: 'POST',
            dataType: 'html',
            data: j_form.serialize(),
            success: function(data){
                j_form.closest('.stream_li').replaceWith(data);
            },
            error: function(xhr, textstatus, err){
                if(403 === xhr.status){
                    var j_replace = $(xhr.responseText);
                    rcp.l(j_replace);
                    j_form.replaceWith(j_replace);
                    j_replace.show();
                }
            }
        });
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
    
    nemo.stream = {};
    nemo.stream.init = function(){
        j_stream = $('.stream');
        var j_form = $('.wishform.off'),
            j_content = j_form.find('textarea'),
            PLACEHOLDER = j_content.attr('placeholder');
        
        j_content.one('focus', function(evt){
            if(j_content.val() === PLACEHOLDER){
                j_content.val('');
            }
        });
        
        j_content.on({
            'focus': function(evt){
                j_form.removeClass('off');
            },
            'blur': function(evt){
                if('' === j_content.val()){
                    j_form.addClass('off');
                }
            }
        });
        
        j_form.on('submit', function(evt){
            evt.preventDefault();
            
            $.ajax(j_form.attr('action'), {
                type: 'POST',
                dataType: 'html',
                data: j_form.serialize(),
                success: function(data){
                    j_stream.prepend(data);
                    j_content.val('').trigger('blur');
                }
            });
        });
        
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
            }).
            delegate('.wishform, .responseform', 'submit', hijax_form_submit);
        
        j_stream.load(nemo.uri_root+'list/' + j_stream.attr('type') + '/');
    };
})(jQuery);