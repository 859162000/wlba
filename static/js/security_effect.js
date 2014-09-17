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

    }

    Ball.prototype.draw = function() {
        this.ball = this.paper.circle(this.x, this.y, this.width, this.height);
        this.ball.attr(this.property);
        this.textElement = this.paper.text(this.x, this.y+2, this.text);
        this.textElement.attr(this.textProperty);

        this.set.push(this.ball);
        this.set.push(this.textElement);
    };


    function Funnel(selector, context) {
        this.context = context;
        this.funnel = $(selector, this.context);
    }

    Funnel.prototype.fadeToColor = function() {
        var funnel = this.funnel,
            context = this.context;
        if(funnel.attr('data-active') && funnel.attr('data-active') == 1) {
            return;
        }
        funnel.attr('data-active', 1);
        funnel.fadeTo(1000, 0.2, function() {
            funnel.removeClass('gray').addClass('color').fadeTo(1000, 1, function() {
                 $('.guarantee-list-item', context).css('visibility', 'visible').addClass('fadeInUp');
            });
        });
    };


    function Roll(ball, props) {
        this.ball = ball;
        this.props = props;
        this._transfer();
        this.init();
    }

    Roll.prototype.init = function() {
        var animations = this.animations,
            ball = this.ball,
            _self = this,
            current = null,
            reference = null;

        this.start = new Animation(ball, animations[0]),
        reference = this.start;

        for(var i = 1; i < animations.length; i++) {
            current = new Animation(ball, animations[i]);
            reference.setNext(current);
            reference = current;
        }

        current.setComplete(function() {
            for(var i = 0, len = _self.events.length; i < len; i++) {
                _self.context.trigger(_self.events[i]);
            }
        });
    };

    Roll.prototype.move = function() {
        this.start.move();
    };

    Roll.prototype.setDispach = function(context, events) {
        this.context = context;
        this.events = events;
    };

    Roll.prototype._transfer = function() {
        var start = [0, 0],
            props = this.props,
            current = start,
            animations = [];

        for(var i = 0, len = props.length; i < len; i++) {
            var coord = this._getEnd(current, props[i].direction, props[i].distance);
            animations.push({transform: coord.str, time: props[i].time});
            current = coord.coord;
        }
        this.animations = animations;
    };

    Roll.prototype._getEnd = function(source, direction, distance) {
        var diameter = 9,
            degree,
            perimeter = Math.PI * diameter;
        switch(direction) {
            case 0:
                source[0] += distance;
                degree = distance * 360 / perimeter;
                break;
            case 1:
                source[1] += distance;
                degree = distance * 360 / perimeter;
                break;
            case 2:
                source[0] -= distance;
                degree = -distance * 360 / perimeter;
                break;
            case 3:
                source[1] -= distance;
                degree = -distance * 360 / perimeter;
                break;

        }
        return {str: 't' + source.join(',') + 'r' + degree, coord: source};

    }


    function Animation(ball, prop) {
        this.ball = ball;
        this.prop = prop;
    }


    Animation.prototype.move = function() {
        var next = this.next,
            complete = this.complete,
            prop = this.prop;
        this.ball.set.stop().animate({transform: prop.transform}, prop.time, function() {
            next && next.move.call(next);
            complete && complete.call(null);
        });
    }

    Animation.prototype.setComplete = function(complete) {
        this.complete = complete;
    };

    Animation.prototype.setNext = function(next) {
        this.next = next;
        return this.next;
    };


    var pipeline_01 = function() {
        var paper = Raphael("pipeline_01", '100%', 220),
            property = {fill: "#fff", stroke: "#fff"};

        var ball = new Ball(165, 9, paper);

        $('.project').on('rollcomplete', function() {
            var funnel = new Funnel('.funnel_02', $('.project'));
                funnel.fadeToColor();
        });

        return {
            animate: function() {
                if(!$('.organization').hasClass('untreated')) {
                    return;
                }
                $('.organization').removeClass('untreated');
                ball.draw();

                var animations = [
                    {distance: 90, direction: 1, time: 500},
                    {distance: 738, direction: 0, time: 5000},
                    {distance: 140, direction: 1, time: 500}
                ]
                var roll = new Roll(ball, animations);
                roll.setDispach($('.project'), ['rollcomplete']);
                roll.move();

            }
        }

    };

    var pipeline_02 = function() {
        var paper = Raphael("pipeline_02", '100%', 475),
            property = {fill: "#fff", stroke: "#fff"};

        var ball = new Ball(905, 219, paper);

        $('.online').on('rollcomplete', function() {
            var funnel = new Funnel('.funnel_03', $('.online'));
                funnel.fadeToColor();
        });

        return {
            animate: function() {

                if(!$('.online').hasClass('untreated')) {
                    return;
                }
                $('.online').removeClass('untreated');
                ball.draw();

                var animations = [
                    {distance: 167, direction: 1, time: 500},
                    {distance: 738, direction: 2, time: 5000},
                    {distance: 103, direction: 1, time: 500}
                ]
                var roll = new Roll(ball, animations);
                roll.setDispach($('.online'), ['rollcomplete']);
                roll.move();

            }
        }

    };


    var pipeline_03 = function() {
        var paper = Raphael("pipeline_03", '100%', 600),
            property = {fill: "#fff", stroke: "#fff"};


        var ball1 = new Ball(137, 19, paper);

        ball1.roll = function(callback) {
            var diameter = 9,
                _self = this,
                perimeter = Math.PI * diameter;

            var degree = 700 * 360 / perimeter;

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
        };

        return {
            animate: function() {
                if(!$('.overdue').hasClass('untreated')) {
                    return;
                }
                $('.overdue').removeClass('untreated');
                ball1.draw();
                ball2.draw();

                ball1.roll();

                ball2.roll(function() {
                    var funnel = new Funnel('.gear', $('.overdue'));
                    funnel.fadeToColor();
                });


            }
        }

    };

    //管道

    var pipe_01 = pipeline_01();
    var pipe_02 = pipeline_02();
    var pipe_03 = pipeline_03();



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
        var funnel = new Funnel('.funnel_01', $('.organization'));
        funnel.fadeToColor();
    };

    var module_07 = new Module(500, '.project');
    module_07.animate = function () {
        if(!$('#organization').hasClass('hidden')) {
            pipe_02.animate();
        }
    };

    var module_09 = new Module(400, '.overdue');
    module_09.animate = function () {
        if(!$('#organization').hasClass('hidden')) {
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
    page.register(module_09);
    page.register(module_10);
    page.register(module_11);


    $.effect = page;

});