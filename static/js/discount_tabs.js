(function() {
    require.config({
        paths: {
            jquery: 'lib/jquery.min'
        }
    });

    require(['jquery'], function ($) {
        return $(document).ready(function () {
            $('.discount--tabs li').hover(function () {
                $(this).addClass('hover').siblings().removeClass('hover');
                var show_tab_main = $(this).attr('data-tabName');
                $('.'+show_tab_main+'').show().siblings().hide();
            });
        })
    })
}).call(this);