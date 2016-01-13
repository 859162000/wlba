org.finance = (function (org) {
    var lib = {
        init: function () {

            var swiper = new Swiper('.swiper-container', {
                paginationClickable: true,
                direction: 'vertical',
                initialSlide : 2,
            });
        }
    }
    return {
        init: lib.init
    }
})(org);

;
(function (org) {
    $.each($('script'), function () {
        var src = $(this).attr('src');
        if (src) {
            if ($(this).attr('data-init') && org[$(this).attr('data-init')]) {
                org[$(this).attr('data-init')].init();
            }
        }
    })
})(org);