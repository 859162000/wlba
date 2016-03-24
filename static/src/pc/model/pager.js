    define(['jquery'], function ($) {
        var list = '', num_pages, number_minus, number_add, ellipsis;
        var pager = function(pager){
            list += "<ul class='pager-target' data-active-page="+pager.page+">";
            if(pager.page > 1){
                list += "<li data-index='prev' class='pager-prev'><a href='javascript:void(0)'><i class='iconfont icon icon-flip-left'></i></a></li>";
            }

            if( pager.pagenumber <= 10){
                num_pages = pager.pagenumber + 1
                for(var i =1 ; i< num_pages; i++){
                    if(pager.page == i){
                        list += "<li data-index="+i+" class='pager-page-number active'><a href='javascript:void(0)'>"+i+"</a></li>"
                    }else{
                        list += "<li data-index="+i+" class='pager-page-number'><a href='javascript:void(0)'>"+i+"</a></li>"
                    }
                }
            }else{

                if(pager.page == 1){
                    list += "<li data-index='1' class='pager-page-number active'><a href='javascript:void(0)'>1</a></li>"
                }else{
                    list += "<li data-index='1' class='pager-page-number'><a href='javascript:void(0)'>1</a></li>"
                }

                if(pager.page >= 5){
                    list += "<li data-index='...' class='pager-page-ellipsis'><a href='javascript:void(0)'>...</a></li>"
                }
                number_minus = pager.page - 2
                number_add = pager.page + 3
                if(number_minus < 2){
                    number_minus = 2
                    number_add = number_add +1
                }
                if(number_add > pager.pagenumber){
                    number_add = pager.pagenumber;
                }

                if(pager.page == pager.pagenumber){
                    number_minus = number_minus -1
                }
                for(var i = number_minus; i< number_add; i++){
                    if(pager.page == i){
                        list += "<li data-index="+i+" class='pager-page-number active'><a href='javascript:void(0)'>"+i+"</a></li>"
                    }else{
                        list += "<li data-index="+i+" class='pager-page-number'><a href='javascript:void(0)'>"+i+"</a></li>"
                    }
                }

                ellipsis = pager.pagenumber - pager.page

                if(ellipsis >= 4){
                    list += "<li data-index='...' class='pager-page-ellipsis'><a href='javascript:void(0)'>...</a></li>"
                }

                if(pager.page == pager.pagenumber){
                    list += "<li data-index="+pager.pagenumber+" class='pager-page-number active'><a href='javascript:void(0)'>"+pager.pagenumber+"</a></li>"
                }else{
                    list += "<li data-index="+pager.pagenumber+" class='pager-page-number'><a href='javascript:void(0)'>"+pager.pagenumber+"</a></li>"
                }
                list += ""
            }

            if(pager.page < pager.pagenumber){
                list += "<li data-index='next' class='pager-next'><a href='javascript:void(0)'><i class='iconfont icon icon-flip-right'></i></a></li>";
            }

            list += '</ul>';

            $('.c-h-pager').html(list);
        }

        var render = function(pager, callback){
            var pagerHTML = pager(pager)

            $('.pager-target li').off('click').on('click', '.c-h-pager', function(){
                var page = $(this).data('index')

                pager({

                })
            })

        };

        return {
            pager: render
        }
    });