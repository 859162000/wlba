require(['jquery'], function( $ ) {
    $.each($('.description'),function(i,o){
        var str = $(o).text()
        if(str.length > 100){
            $(o).text($(o).text().substring(0,100)+'...')
        }
    })
    $.each($('.contentA'),function(i,o){
        var str = $(o).text()
        if(str.length > 100){
            $(o).text($(o).text().substring(0,130)+'...')
        }
    })
})