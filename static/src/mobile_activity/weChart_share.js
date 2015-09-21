


org.weChatStart = (function(org){
    var lib = {
        init:function(){
            console.log('start')
        },
    }
    return {
        init : lib.init
    }
})(org);

org.weChatDetail = (function(org){
    var lib = {
        init:function(){
            console.log('detail')
        },
    }
    return {
        init : lib.init
    }
})(org);

org.weChatEnd = (function(org){
    var lib = {
        init:function(){
            console.log('end')
        },
    }
    return {
        init : lib.init
    }
})(org);

;(function(org){
    $.each($('script'), function(){
        var src = $(this).attr('src');
        if(src){
            if($(this).attr('data-init') && org[$(this).attr('data-init')]){
                org[$(this).attr('data-init')].init();
            }
        }
    })
})(org);