require.config({
  paths: {
    'videojs': 'lib/video.min',
    'lightbox':'lib/lightbox-2.6.min'
  },
  shim: {
    'lightbox': ['jquery'],
    'videojs': ['jquery']
  }
});

require(['jquery', 'lightbox'], function( $ , lightbox){
    var DEFAULT_VERSION = "8.0",
        ua = navigator.userAgent.toLowerCase(),
        isIE = ua.indexOf("msie")>-1,
        safariVersion;
    if(isIE){
        safariVersion =  ua.match(/msie ([\d.]+)/)[1];
        if(safariVersion <= DEFAULT_VERSION ){
        }else{
            require(['videojs'])
        }
    }else{
        require(['videojs'])
    }
    /*认识网利宝*/
    $('.c_nav a').hover(function(){
        var index = $(this).index();
        $('.c_content').hide().eq(index).show();
        $('.c_nav a').removeClass('active');
        $(this).addClass('active');
    })

    /*网利风采*/
    var box = $('.staff_photos'),
        item = $('.staff_style_box'),
        widths = item.width()*item.length;
    box.width(widths);
    /*下一页*/
    $('.next_page').on('click',function(){
        var self = $(this);
        if(!self.hasClass('onClick')){
            var left = Math.round(box.position().left);
            self.addClass('onClick');
            console.log(left+'ddddddd'+(widths-item.width()))
            left == -(widths-item.width()) ? (box.stop().animate({'left' : 0},500,function(){self.removeClass('onClick')})) : (box.stop().animate({'left' : left - item.width()},500,function(){self.removeClass('onClick')}))
        }
    })
    /*上一页*/
    $('.pre_page').on('click',function(){
        var self = $(this);
        if(!self.hasClass('onClick')) {
            var left = Math.round(box.position().left);
            self.addClass('onClick');
            left == 0 ? box.stop().animate({'left': -(widths - item.width())},500, function(){self.removeClass('onClick')}) : box.stop().animate({'left': left + item.width()},500,function(){self.removeClass('onClick')})
        }
    })

    $('.staff_style_boxs').hover(function(){
        $(this).parent().addClass('photo_hover')
    },function(){
        $(this).parent().removeClass('photo_hover')
    })

    //招聘信息
    $('.job_title_h').on('click',function(){
        var self = $(this);
        $('.job_title_h').not(this).next().slideUp();$('.job_title_h i').removeClass('open');self.find('i').toggleClass('open')
        self.next().slideToggle('fast',function(){
            if(self.next().is(':hidden')){
                self.find('i').removeClass('open');
            }
        });
    })
    $('.job_class span').click(function(){
        var parent = $('.job_list_c'),text = $(this).text();
        $('.job_class').find('.active').removeClass('active');$(this).addClass('active');parent.find('.job_detail').slideUp();$('.job_title_h i').removeClass('open');
        if(text == '全部'){
            parent.find('.job_title_h').show();
        }else{
            parent.find('.job_title_h').hide();
            parent.find('.job_title_h[data-type="'+ $(this).text() +'"]').show();
        }
    })
});