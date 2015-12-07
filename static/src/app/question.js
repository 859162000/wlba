org.result = (function (org) {
    var lib = {
        init: function () {
            $('.question-list').on('click', function(){
                $(this).siblings('.question-answer').toggle()
                $(this).find('.question-arrow').toggleClass('question-arrow-rotate')
            })
        },
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