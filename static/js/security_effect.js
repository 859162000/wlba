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
                        distance = $('.security-bar-container').offset().top - $(window).scrollTop(),
                        tabDistance = $('#organization').offset().top - $(window).scrollTop();

                    if (distance < 0) {
                        $('.security-bar').css('position', 'fixed');
                    } else {
                        $('.security-bar').css('position', '');
                    }

                    if(tabDistance > 50) {
                        $('.security-bar a').removeClass('active')
                        $('.security-bar a[href="#platform"]').addClass('active')
                    } else {
                        $('.security-bar a').removeClass('active')
                        $('.security-bar a[href="#organization"]').addClass('active')
                    }
                }
            }
        };
        /*
        function PipePart(config, paper) {
            this.start = config.start;
            this.end = config.end;
            this.paper = paper;
        }

        PipePart.prototype.draw = function() {
            console.log(this.start);
            this.rect = this.paper.rect.apply(this.paper, this.start);
        }

        PipePart.prototype.animate = function() {
            console.log('rect', this.rect)
            this.rect.stop().animate.apply(this.paper, this.end);
        }

        var pipeline = function () {
            var speed = 50,
                step = 5;
            var paper = Raphael("pipeline_01", '100%', 200),
                parts = [],
                st = paper.set();
            parts.push(new PipePart({start: [150, 0, 30, 100], end: [{y: 80, height: 0}, 500]}, paper));
            return {
                init: function() {
                    for(var i = 0, len = parts.length; i < len; i++) {
                        parts[i].draw();
                    }
                },
                animate: function() {
                    parts[0].animate();
                }
            };

        };
        */
        var pipeline_01 = function() {
            var paper = Raphael("pipeline_01", '100%', 200),
                property = {fill: "#fff", stroke: "#fff"},
                rect_01,
                rect_02,
                rect_03;

            rect_01 = paper.rect(150, 0, 30, 100);
            rect_01.attr(property);

            rect_02 = paper.rect(150, 80, 780, 30);
            rect_02.attr(property);

            rect_03 = paper.rect(880, 100, 50, 80);
            rect_03.attr(property);

            return {
                animate: function() {
                    $('.organization').removeClass('untreated');
                    rect_01.stop().animate({y: 80, height: 0}, 1000, 'linear', function() {
                        rect_02.stop().animate({x: 930, width: 0}, 1000, 'linear', function() {
                            rect_03.stop().animate({y: 180, height: 0}, 1000, 'linear', function() {
                                $('.project').removeClass('untreated');
                            });
                        })
                    });

                }
            }

        };

        var pipeline_02 = function() {
            var paper = Raphael("pipeline_02", '100%', 475),
                property = {fill: "#fff", stroke: "#fff"},
                rect_01,
                rect_02,
                rect_03;

            rect_01 = paper.rect(880, 188, 50, 180);
            rect_01.attr(property);

            rect_02 = paper.rect(140, 355, 780, 30);
            rect_02.attr(property);

            rect_03 = paper.rect(140, 355, 50, 100);
            rect_03.attr(property);

            return {
                animate: function() {

                    rect_01.stop().animate({y: 368, height: 0}, 1000, 'linear', function() {
                        rect_02.stop().animate({x: 150, width: 0}, 1000, 'linear', function() {
                            rect_03.stop().animate({y: 455, height: 0}, 1000, 'linear', function() {
                                $('.online').removeClass('untreated');
                            });
                        })
                    });


                }
            }

        };


        var pipeline_03 = function() {
            var paper = Raphael("pipeline_03", '100%', 600),
                property = {fill: "#fff", stroke: "#fff"},
                rect_01,
                rect_02,
                rect_03;

            rect_01 = paper.rect(170, 10, 30, 70);
            rect_01.attr(property);

            rect_02 = paper.rect(170, 80, 755, 30);
            rect_02.attr(property);

            rect_03 = paper.rect(880, 110, 50, 60);
            rect_03.attr(property);

            rect_04 = paper.rect(880, 360, 50, 140);
            rect_04.attr(property);

            rect_05 = paper.rect(630, 460, 250, 50);
            rect_05.attr(property);


            rect_06 = paper.rect(120, 10, 30, 485);
            rect_06.attr(property);

            rect_07 = paper.rect(150, 460, 300, 50);
            rect_07.attr(property);





            return {
                animate: function() {

                    rect_01.stop().animate({y: 80, height: 0}, 500, 'linear', function() {
                        rect_02.stop().animate({x: 920, width: 0}, 1000, 'linear', function() {
                            rect_03.stop().animate({y: 170, height: 0}, 500, 'linear', function() {
                                $('.gear').removeClass('untreated');
                                rect_04.stop().animate({y: 500, height: 0}, 500, 'linear', function() {
                                    rect_05.stop().animate({x: 630, width: 0}, 1000, 'linear');
                                });
                            });
                        })
                    });

                    rect_06.stop().animate({y: 500, height: 0}, 2000, 'linear', function() {
                        rect_07.stop().animate({x: 450, width: 0}, 1500, 'linear', function() {
                            $('.investor').removeClass('untreated');
                        });
                    });


                }
            }

        };

        //管道
        //var module_07 = new Module(300, '.');

        //var pipes = pipeline();
        //pipes.init();
        var pipe_01 = pipeline_01();
        var pipe_02 = pipeline_02();
        var pipe_03 = pipeline_03();



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

        $.fn.bounceIn = function() {
            if(this.attr('data-active') == 1) {
                return;
            }
            this.attr('data-active', '1');
            var image = this,
                normalWidth = image.width(),
                zoomInWidth = normalWidth + normalWidth*0.2,
                zoomOutWidth = normalWidth - normalWidth*0.1;
                zoomIn = function() {
                    image.animate({ width: zoomInWidth }, 200, restore);
                },

                restore = function() {
                    image.animate({ width: normalWidth }, 200, function() {
                        image.removeAttr('data-active');
                    });
                }
            image.animate({ width: zoomOutWidth }, 200, zoomIn);
        }


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

        var module_01 = new Module(400, '.organization');
        module_01.animate = function () {
            $(this.selector).css('visibility', 'visible')
            $('.guarantee-list-item', $(this.selector)).addClass('fadeInUp');
        };

        var module_07 = new Module(400, '.project');
        module_07.animate = function () {
            if(!$('#organization').hasClass('hidden')) {
                $(this.selector).css('visibility', 'visible')
                $('.guarantee-list-item', $(this.selector)).addClass('fadeInUp');
                pipe_02.animate();
            }
        };

        var module_08 = new Module(400, '.online');
        module_08.animate = function () {
            if(!$('#organization').hasClass('hidden')) {
                $(this.selector).css('visibility', 'visible')
                $('.guarantee-list-item', $(this.selector)).addClass('fadeInUp');
            }
        };

        var module_09 = new Module(400, '.overdue');
        module_09.animate = function () {
            if(!$('#organization').hasClass('hidden')) {
                $(this.selector).css('visibility', 'visible')
                $('.guarantee-list-item', $(this.selector)).addClass('fadeInUp');
                pipe_03.animate();

            }
        };



        var module_02 = new Module(50, '.pipeline_01');
        module_02.animate = function () {
            if(!$('#organization').hasClass('hidden')) {
                pipe_01.animate();
            }

        };

        var module_10 = new Module(50, '.platform_01');
        module_10.animate = function () {
            if(!$('#platform').hasClass('hidden')) {
                $(this.selector).css('visibility', 'visible');
                var _self = this;
                $('.animation_01', $(this.selector)).addClass('fade-in-left');
                setTimeout(function(){
                    $('.animation_02', $(_self.selector)).css('visibility', 'visible');
                    $('.animation_02', $(_self.selector)).addClass('bounceIn');
                }, 500);
            }
        };

        var module_03 = new Module(200, '.platform_02');
        module_03.animate = function () {
            if(!$('#platform').hasClass('hidden')) {
                $(this.selector).css('visibility', 'visible');
                var _self = this;
                $('.animation_05', $(this.selector)).addClass('fade-in-right');
                $(this.selector).checked();
                $('.animation_03', $(_self.selector)).css('visibility', 'visible');
                $('.animation_03', $(_self.selector)).addClass('fade-in-left');

                //setTimeout(function(){
                    $('.animation_04', $(_self.selector)).css('visibility', 'visible');
                    //$('.animation_04', $(_self.selector)).addClass('bounceIn');
                //}, 1000);
            }
        };

        var module_04 = new Module(200, '.platform_03');
        module_04.animate = function () {
            if(!$('#platform').hasClass('hidden')) {
                $(this.selector).css('visibility', 'visible');
                var _self = this;
                $('.animation_06', $(this.selector)).addClass('fade-in-left');
                $('.animation_07', $(this.selector)).addClass('fade-in-right');
                $(this.selector).checked();
                setTimeout(function(){
                    $('.animation_08', $(_self.selector)).css('visibility', 'visible');
                    $('.animation_08', $(_self.selector)).addClass('fade-to-small');
                }, 500);
            }
        };

        var module_05 = new Module(200, '.platform_04');
        module_05.animate = function () {
            if(!$('#platform').hasClass('hidden')) {
                $(this.selector).css('visibility', 'visible');
                var _self = this;
                $('.animation_11', $(this.selector)).addClass('fade-in-right');
                $(this.selector).checked();
                setTimeout(function(){
                    $('.animation_09', $(_self.selector)).css('visibility', 'visible');
                    $('.animation_09', $(_self.selector)).addClass('fadeInDown');
                    setTimeout(function() {
                        $('.animation_10', $(_self.selector)).css('visibility', 'visible');
                        $('.animation_10', $(_self.selector)).addClass('fade-to-small');
                    }, 200)
                }, 200);
            }
        };

        var module_06 = new Module(200, '.platform_05');
        module_06.animate = function () {
            if(!$('#platform').hasClass('hidden')) {
                $(this.selector).css('visibility', 'visible');
                var _self = this;
                $('.animation_12', $(this.selector)).addClass('fade-in-left');
                $(this.selector).checked();
                setTimeout(function(){
                    $('.animation_13', $(_self.selector)).css('visibility', 'visible');
                    $('.animation_13', $(_self.selector)).addClass('fade-to-small');
                }, 500);
            }
        };

        var module_11 = new Module(200, '.platform_06');
        module_11.animate = function () {
            if(!$('#organization').hasClass('hidden')) {
                $(this.selector).css('visibility', 'visible');
                var _self = this;
                $('.animation_14', $(this.selector)).addClass('fade-in-left');
                $('.animation_16', $(this.selector)).addClass('fade-in-right');
                setTimeout(function(){
                    $('.animation_15', $(_self.selector)).css('visibility', 'visible');
                    $('.animation_15', $(_self.selector)).addClass('fade-in');
                }, 500);
            }
        };



        var page = control();
        page.register(module_01);
        page.register(module_02);

        page.register(module_03);
        page.register(module_04);
        page.register(module_05);
        page.register(module_06);
        page.register(module_07);
        page.register(module_08);
        page.register(module_09);
        page.register(module_10);
        page.register(module_11);


        $.effect = page;

    //});
});