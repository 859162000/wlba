
require(['jquery', 'echarts', './model/pager', './model/date', 'csrf'], function ($, echarts) {

     $.post('/api/uc/repayment_plan/', {start_submit: '2015-1-1', end_submit: '2016-1-1',page: 1, pagesize: 10  })
        .done(function(result){
            console.log(result)
            $('.center-from-home').html(result.html_data)
        })

        .fail(function(){

        })



    var $startDate = $('.start-date'),
            $endDate = $('.end-date');

    $startDate.pickadate({
        hiddenPrefix: 'start'
    })
    $endDate.pickadate({
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