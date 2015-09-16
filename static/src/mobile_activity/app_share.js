
org.lottery = (function(){
    var lib = {
        init :function(){

        }
    };
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
