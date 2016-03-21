require(['jquery'], function( $ ) {
    var str1= '[图片]',str2 = '[视频]';
    $.each($('.description'),function(i,o){
        labelToStr($(o),95);
    })
    $.each($('.contentA'),function(i,o){
        labelToStr($(o),130)
    })
    function labelToStr(obj,counts){
        var str = obj.html(),
            img = obj.find('img'),
            embed = obj.find('embed');
        if(img.length > 0){
            img.before(('<span>'+str1+'</span>'));
            img.remove();
        }
        if(embed.length > 0){
            embed.before(('<span>'+str2+'</span>'));
            embed.remove();
        }
        if(str.length > counts){
            //if(obj.find('p').first().text().length > counts || obj.find('p').length > 2){
            //    obj.parent().find('.link').addClass('link-p');
            //}
            obj.html($.trim(obj.html()).substring(0,counts)+'...')
        }
    }
})