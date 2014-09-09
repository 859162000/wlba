/**
 * Created by taohe on 14-9-7.
 */
require.config({
  paths: {
      jquery: 'lib/jquery.min',
      raphael: 'lib/raphael-min'
  }
});
require(['jquery', 'raphael'], function($, raphael) {

    //$(function () {
        //1. page control
        var control = function () {
            var modules = [];
            return {
                getModules: function () {
                    return modules;
                },
                //1.1 注册module
                register: function (module) {
                    modules.push(module);
                },
                //1.2 派发和触发module事件
                dispatch: function () {
                    for (var i = 0; i < modules.length; i++) {
                        modules[i].showEffect();
                    }
                },
                setTabBar: function () {
                    var wheight = $(window).height(),
                        distance = $('.security-bar-container').offset().top - $(window).scrollTop();

                    if (distance < 0) {
                        $('.security-bar').css('position', 'fixed');
                    } else {
                        $('.security-bar').css('position', '');
                    }
                }
            }
        };

        var pipeline = function () {
            var speed = 50,
                step = 5;

        };

        $.fn.checked = function () {
            var arr = [],
                step = 1,
                speed = 20,
                width = 22,
                orders = 0;
            $('.icon-circle', this).each(function (index, item) {
                arr.push($(item));
            });
            var show = function () {
                var mark = $('.icon-check-mark', arr[orders]);
                mark.width(mark.width() + step);
                if (mark.width() >= width) {
                    orders++;
                }
                if (orders < arr.length) {
                    setTimeout(show, speed);
                }
            };
            show();
        };


        //2. module
        function Module(distance, selector) {
            this.distance = distance;
            this.selector = selector;
        }

        //2.1 显示
        Module.prototype.show = function () {
            this.animate && this.animate.call(this, arguments)
        };
        //2.2 隐藏
        Module.prototype.hide = function () {
        };

        //2.3 是否显示动画效果
        Module.prototype.showEffect = function () {
            if (this.getDistanceFromBottom() >= this.distance) {
                this.show();
            }
        };

        Module.prototype.getDistanceFromBottom = function () {
            var wheight = $(window).height(),
                distance = $(this.selector).offset().top - $(window).scrollTop();
            return wheight - distance;
        };

        //3 动画实例

        var module_01 = new Module(200, '.organization');
        module_01.animate = function () {
            $(this.selector).css('visibility', 'visible')
            $('.guarantee-list-item', $(this.selector)).addClass('fadeInUp');
        };

        var module_02 = new Module(50, '.pipeline_01');
        module_02.animate = function () {
            var paper = Raphael("pipeline_01");
            var rect1 = paper.rect(150, 0, 30, 100);
            rect1.attr('fill', '#fff');
            rect1.attr('stroke', '#fff');

            var rect2 = paper.rect(150, 80, 870, 30);
            rect2.attr('fill', '#fff');
            rect2.attr('stroke', '#fff');

            var rect3 = paper.rect(840, 80, 30, 80);
            rect3.attr('fill', '#fff');
            rect3.attr('stroke', '#fff');

        };

        var module_03 = new Module(300, '.platform_02');
        module_03.animate = function () {
            $(this.selector).checked();
        };

        var module_04 = new Module(400, '.platform_03');
        module_04.animate = function () {
            $(this.selector).checked();
        };

        var module_05 = new Module(400, '.platform_04');
        module_05.animate = function () {
            $(this.selector).checked();
        };

        var module_06 = new Module(400, '.platform_05');
        module_06.animate = function () {
            $(this.selector).checked();
        };

        //管道
        //var module_07 = new Module(300, '.');

        var page = control();
        page.register(module_01);
        page.register(module_02);

        page.register(module_03);
        page.register(module_04);
        page.register(module_05);
        page.register(module_06);


        $.effect = page;

    //});
});