require.config({
    paths: {
        'picker': 'lib/picker',
        'picker.date': 'lib/picker.date',
        'echarts': 'lib/echarts.min',
    },
    shim: {
        'picker.date': ['jquery'],
        'picker': ['jquery'],

    }
});

require(['jquery', 'echarts', 'picker', 'picker.date', ], function ($, echarts) {
    $.extend($.fn.pickadate.defaults, {
        format: 'yyyy-mm-dd',
        formatSubmit: 'yyyy-mm-dd',
        monthsFull: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
        monthsShort: ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二'],
        weekdaysFull: ['一', '二', '三', '四', '五', '六', '七'],
        weekdaysShort: ['一', '二', '三', '四', '五', '六', '七'],
        //selectMonths: true,
        selectYears: true,
        today: '今天',
        clear: '清除',
        close: '关闭',
    });

    $('.start-date').pickadate({
        hiddenPrefix: 'start'
    })
     $('.end-date').pickadate({
        hiddenPrefix: 'end'
    })

    var type = echarts.init(document.getElementById('type'));
    var limit = echarts.init(document.getElementById('limit'));
    var earning = echarts.init(document.getElementById('earning'));


    var a = 1
    option = {
        title: {
            text: '项目类型',
            top: 160,
            left: 40,
            textStyle: {
                fontSize: 14,
                color: '#666',
                fontWeight: 'normal'
            }
        },
        tooltip: {
            trigger: 'item',
            formatter: "{b}{c}个",
            padding: [5, 20]
        },
        legend: {
            itemGap: 5,
            itemWidth: 10,
            top: 185,
            left: 40,
            icon: 'circle',
            orient: 'vertical',
            data:["散标投资",'月利宝','债权转让'],
            formatter: function(name){
                a++;
                return a + name
            },
            textStyle: {
             color: '#b2b2b2'
            },

        },
        series: [
            {
                type:'pie',
                radius: ['50%%', '80%'],
                center: ['50%', '30%'],
                hoverAnimation: true,
                label: {
                    normal: {
                        show: false,
                        position: 'center'
                    },

                },
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                data:[
                    {
                        value:35,
                        name:'散标投资',
                        itemStyle: {
                            normal: {
                                color: '#f2b98b'
                            }

                        }
                    },
                    {
                        value:310,
                        name:'月利宝',
                        itemStyle: {
                            normal: {
                                color: '#a0c2f2'
                            }

                        }
                    },
                    {
                        value:310,
                        name:'债权转让',
                        itemStyle: {
                            normal: {
                                color: '#c9d8a0',
                            }
                        }
                    }
                ],

            }
        ]
    };

    type.setOption(option);
    limit.setOption(option);
    earning.setOption(option);

});