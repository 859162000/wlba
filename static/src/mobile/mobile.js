
var org = (function(){
    var lib = {
        scriptName: 'mobile.js',
        test :function(){
            console.log('test')
        }
    }
    return {
        scriptName : lib.scriptName
    }
})()

//list
var list = (function(org){
    var list = {
        windowHeight : $(window).height(),
        domHeight : document.body.clientHeight,
        scrollTop : document.body.scrollTop,
        canGetPage : false,
        scale : 0.7,
        pageNum: 1,
        init :function(){
            //list._scrollListen();
            list._getNextPage();
        },
        _scrollListen:function(){
            $(document).scroll(function(){
                if(list.scrollTop / (list.domHeight -list.windowHeight ) >= list.scale){
                    list._getNextPage();
                }
            });
        },
        _getNextPage :function(){
            $.ajax({
                type: 'GET',
                url: '/api/p2ps/wx',
                success: function(data){
                   console.log(data)
                },
                error: function(xhr, type){
                    alert('Ajax error!')
                }
            })
        }

    };
    return {
        init : list.init
    }
})(org)


~(function(org){
    $.each($("script"), function(index, item){
      if($(this).attr("src").indexOf(org.scriptName) > 0){
        if($(this).attr("data-init") && window[$(this).attr("data-init")]){
            window[$(this).attr("data-init")].init()
        }
      }
    })
})(org)
