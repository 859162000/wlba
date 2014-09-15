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

        var ball = function() {
            var obj = $('.ball'),
                diameter = obj.height(),
                perimeter = Math.PI * diameter,
                is = false;

            return {
                rotateBall: function(distance) {
                    if(is) {
                        return;
                    }
                    is = true;
                    var degree = distance * 360 / perimeter;
                    obj.css({
                        transition: ".7s cubic-bezier(1.000, 1.450, 0.185, 0.850)",
                        transform: 'translateY('+ distance +'px)'
                    }).find('div').css({
                        transition: ".7s cubic-bezier(1.000, 1.450, 0.185, 0.850)",
                        transform: 'rotate(' + degree + 'deg)'
                    });
                    is = false;
                },
                rolling: function(distance) {
                    var degree = distance * 360 / perimeter,
                        leftx = parseInt(obj.css('left'));
                    obj.animate({
                        left: '+=' + leftx,
                        rotate: degree + 'deg'
                    }, 1000);
                },
                start: function() {

                }
            };
        };

        function Ball(x, y, paper) {
            this.x = x;
            this.y = y;
            this.paper = paper;

            this.width = 9;
            this.height = 9;

            this.set = this.paper.set();
            this.text = '￥';
            this.textProperty = {fill: '#fff'};
            this.property = {fill: '#ff9c00', stroke: 'none'};

            //this.set.push();
        }

        Ball.prototype.draw = function() {
            this.ball = this.paper.circle(this.x, this.y, this.width, this.height);
            this.ball.attr(this.property);
            this.textElement = this.paper.text(this.x, this.y+2, this.text);
            this.textElement.attr(this.textProperty);

            this.set.push(this.ball);
            this.set.push(this.textElement);
        };

        Ball.prototype.roll = function(callback) {
            var diameter = 9,
                _self = this,
                perimeter = Math.PI * diameter;

            var degree = 700 * 360 / perimeter;

            _self.set.stop().animate({'transform': 't0,90r'+ 20}, 500, function() {
                _self.set.stop().animate({'transform': 't738,90r'+ degree}, 5000, function() {
                    _self.set.stop().animate({'transform': 't738,230r'+ 30}, 500, function() {
                        callback && callback.call(_self)
                    });
                });
            });
        };

        var ball01 = ball();

        var pipeline_01 = function() {
            var paper = Raphael("pipeline_01", '100%', 220),
                property = {fill: "#fff", stroke: "#fff"},
                rect_01,
                rect_02,
                rect_03;


            /*
            rect_01 = paper.rect(150, 0, 30, 100);
            rect_01.attr(property);

            rect_02 = paper.rect(150, 80, 780, 30);
            rect_02.attr(property);

            rect_03 = paper.rect(880, 100, 50, 80);
            rect_03.attr(property);

            var st = paper.set();

            ball = paper.circle(165, 9, 9, 9);
            ball.attr({fill: 'red', stroke: 'none'});
            text = paper.text(165, 11, '￥');
            text.attr({fill: '#fff'});

            st.push(ball);
            st.push(text);
            var diameter = 9,
                perimeter = Math.PI * diameter;

            var degree = 700 * 360 / perimeter;

            st.stop().animate({'transform': 't0,90r'+ 20}, 500, function() {
                st.stop().animate({'transform': 't738,90r'+ degree}, 5000, function() {
                    st.stop().animate({'transform': 't738,190r'+ 30}, 500);
                });
            });
             */

            var ball = new Ball(165, 9, paper);

            return {
                animate: function() {
                    console.log('start');
                    if(!$('.organization').hasClass('untreated')) {
                        console.log('inner');
                        return;
                    }
                    $('.organization').removeClass('untreated');
                    /*
                    rect_01.stop().animate({y: 80, height: 0}, 1000, 'linear', function() {
                        rect_02.stop().animate({x: 930, width: 0}, 1000, 'linear', function() {
                            rect_03.stop().animate({y: 180, height: 0}, 1000, 'linear', function() {
                                $('.project').removeClass('untreated');
                            });
                        })
                    });
                     */

                    //ball01.rolling(87);
                    ball.draw();

                    ball.roll(function() {
                        if($('.funnel_02').attr('data-active') && $('.funnel_02').attr('data-active') == 1) {
                            return;
                        }
                        $('.funnel_02').attr('data-active', 1);
                        var funnel = $('.funnel_02'),
                            _self = $('.project');
                        funnel.fadeTo(1000, 0.2, function() {
                            funnel.removeClass('gray').addClass('color').fadeTo(1000, 1, function() {
                                 $('.guarantee-list-item', $(_self.selector)).css('visibility', 'visible').addClass('fadeInUp');
                            });
                        });
                    });
                    console.log('rolling');

                }
            }

        };

        var pipeline_02 = function() {
            var paper = Raphael("pipeline_02", '100%', 475),
                property = {fill: "#fff", stroke: "#fff"},
                rect_01,
                rect_02,
                rect_03;

            var ball = new Ball(905, 219, paper);
            ball.roll_02 = function(callback) {
                var diameter = 9,
                    _self = this,
                    perimeter = Math.PI * diameter;

                var degree = -700 * 360 / perimeter;

                _self.set.stop().animate({'transform': 't0,167r'+ 20}, 500, function() {
                    _self.set.stop().animate({'transform': 't-738,167r'+ degree}, 5000, function() {
                        _self.set.stop().animate({'transform': 't-738,270r'+ 30}, 500, function() {
                            callback && callback.call(_self)
                        });
                    });
                });
            };

            return {
                animate: function() {

                    if(!$('.project').hasClass('untreated')) {
                        return;
                    }
                    $('.project').removeClass('untreated');
                    ball.draw();

                    ball.roll_02(function() {
                        if($('.funnel_03').attr('data-active') && $('.funnel_03').attr('data-active') == 1) {
                            return;
                        }
                        $('.funnel_03').attr('data-active', 1);
                        var funnel = $('.funnel_03'),
                            _self = $('.online');
                        funnel.fadeTo(1000, 0.2, function() {
                            funnel.removeClass('gray').addClass('color').fadeTo(1000, 1, function() {
                                 $('.guarantee-list-item', $(_self.selector)).css('visibility', 'visible').addClass('fadeInUp');
                            });
                        });

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

            /*
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

            */

            var ball1 = new Ball(137, 19, paper);

            ball1.roll = function(callback) {
                var diameter = 9,
                    _self = this,
                    perimeter = Math.PI * diameter;

                var degree = -700 * 360 / perimeter;

                _self.set.stop().animate({'transform': 't0,465r'+ 20}, 500, function() {
                    _self.set.stop().animate({'transform': 't718,465r'+ degree}, 5000, function() {
                         callback && callback.call(_self)
                    });
                });
            };
            var ball2 = new Ball(190, 19, paper);

            ball2.roll = function(callback) {
                var diameter = 9,
                    _self = this,
                    perimeter = Math.PI * diameter;

                var degree = 700 * 360 / perimeter;

                _self.set.stop().animate({'transform': 't0,75r'+ 20}, 500, function() {
                    _self.set.stop().animate({'transform': 't718,75r'+ degree}, 5000, function() {
                        _self.set.stop().animate({'transform': 't718,170r'+ 30}, 500, function() {
                            callback && callback.call(_self)
                        });
                    });
                });
            }

            console.log('overdue');
            return {
                animate: function() {
                    if(!$('.overdue').hasClass('untreated')) {
                        return;
                    }
                    $('.overdue').removeClass('untreated');
                    ball1.draw();
                    ball2.draw();
                    console.log('overdue');

                    ball1.roll();

                    ball2.roll(function() {
                        if($('.gear').attr('data-active') && $('.gear').attr('data-active') == 1) {
                            return;
                        }
                        $('.gear').attr('data-active', 1);
                        var funnel = $('.gear'),
                            _self = $('.overdue');
                        funnel.fadeTo(1000, 0.2, function() {
                            funnel.removeClass('gray').addClass('color').fadeTo(1000, 1, function() {
                                 $('.guarantee-list-item', $(_self.selector)).css('visibility', 'visible').addClass('fadeInUp');
                            });
                        });
                    });

                    /*
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
                    */

                }
            }

        };

        //管道

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
                normalHeight = image.height(),
                zoomInWidth = normalWidth + normalWidth*0.03,
                zoomOutWidth = normalWidth - normalWidth*0.03;
                this.css('position', 'relative');
                this.wrap('<div class="temp-wrap" style="position:relative"></div>');
                zoomIn = function() {
                    image.animate({ width: zoomOutWidth, left: normalWidth*0.03/2, top:  normalHeight*0.03/2}, 250, restore);
                },

                restore = function() {
                    image.animate({ width: normalWidth, left: 0, top: 0 }, 300, function() {
                        image.removeAttr('data-active');
                        image.css('position', '');
                        image.unwrap();
                    });
                }
            image.animate({ width: zoomInWidth, left: -normalWidth*0.03/2, top: -normalHeight*0.03/2}, 400, restore);
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
            if($('.funnel_01').attr('data-active') && $('.funnel_01').attr('data-active') == 1) {
                return;
            }
            $('.funnel_01').attr('data-active', 1);
            var funnel = $('.funnel_01'),
                _self = this;
            funnel.fadeTo(1000, 0.2, function() {
                funnel.removeClass('gray').addClass('color').fadeTo(1000, 1, function() {
                     $('.guarantee-list-item', $(_self.selector)).css('visibility', 'visible').addClass('fadeInUp');
                });
            });
        };

        var module_07 = new Module(500, '.project');
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



        var module_02 = new Module(500, '.pipeline_01');
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