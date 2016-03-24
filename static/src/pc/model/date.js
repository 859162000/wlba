    define(['jquery', 'picker', 'picker.date'], function ($) {
        $.extend($.fn.pickadate.defaults, {
            format: 'yyyy-mm-dd',
            formatSubmit: 'yyyy-mm-dd',
            monthsFull: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
            monthsShort: ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二'],
            weekdaysFull: ['一', '二', '三', '四', '五', '六', '七'],
            weekdaysShort: ['一', '二', '三', '四', '五', '六', '七'],
            selectYears: 3,
            today: '今天',
            clear: '清除',
            close: '关闭',
        });

        function defaultDate(startTarget, endTarget ){
            var
                filterDate = new Date(),
                year = filterDate.getFullYear(),
                month = filterDate.getMonth() + 1,
                day = filterDate.getDate();

            startTarget.attr('value', (year-1) + '-' + month + '-'+ day)
            endTarget.attr('value', year + '-' + month + '-'+ day)
        }
        function definedDate(startTarget, endTarget, startDate, endDate){
            startTarget.attr('value', startDate)
            endTarget.attr('value', endDate)
        }


        return {
            defaultDate: defaultDate,
            definedDate: definedDate
        }
    });