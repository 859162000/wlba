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

                if(tabDistance > 62) {
                    $('.security-bar a').removeClass('active')
                    $('.security-bar a[href="#platformAnchor"]').addClass('active')
                } else {
                    $('.security-bar a').removeClass('active')
                    $('.security-bar a[href="#organizationAnchor"]').addClass('active')
                }
            }
        }
    };


    function Ball(x, y, paper) {
        this.x = x-9;
        this.y = y-9;
        this.paper = paper;

        this.width = 18;
        this.height = 18;

        this.set = this.paper.set();
        this.text = '￥';
        this.textProperty = {fill: '#fff'};
        this.property = {fill: '#ff9c00', stroke: 'none'};

    }

    Ball.prototype.draw = function() {
        var url = '/static/images/security/ball.png';
        this.ball = this.paper.image(url, this.x, this.y, this.width, this.height);
        //this.ball.attr(this.property);
        //this.textElement = this.paper.text(this.x, this.y+2, this.text);
        //this.textElement.attr(this.textProperty);

        this.set.push(this.ball);
        //this.set.push(this.textElement);
    };

    Ball.prototype.remove = function() {
        this.set.remove();
    };


    function Funnel(selector, context) {
        this.context = context;
        this.funnel = $(selector, this.context);
    }

    Funnel.prototype.fadeToColor = function() {
        var funnel = this.funnel,
            context = this.context,
            time = 1500;
        if(funnel.attr('data-active') && funnel.attr('data-active') == 1) {
            return;
        }
        funnel.attr('data-active', 1);
        funnel.fadeTo(time, 0, function() {
            funnel.removeClass('gray').addClass('color').fadeTo(time, 1, function() {
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
            _self.ball.remove();
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
        var ball2 = new Ball(190, 19, paper);


        $('.overdue').on('rollcomplete1', function() {
            var funnel = new Funnel('.investor', $('.overdue'));
                funnel.fadeToColor();
        });

        $('.overdue').on('rollcomplete2', function() {
            var funnel = new Funnel('.gear', $('.overdue'));
                funnel.fadeToColor();
        });

        return {
            animate: function() {
                if(!$('.overdue').hasClass('untreated')) {
                    return;
                }
                $('.overdue').removeClass('untreated');
                ball1.draw();
                ball2.draw();

                var animations1 = [
                    {distance: 465, direction: 1, time: 1000},
                    {distance: 400, direction: 0, time: 2000}
                ]
                var roll1 = new Roll(ball1, animations1);
                roll1.setDispach($('.overdue'), ['rollcomplete1']);
                roll1.move();


                var animations2 = [
                    {distance: 75, direction: 1, time: 500},
                    {distance: 718, direction: 0, time: 1000},
                    {distance: 390, direction: 1, time: 500},
                    {distance: 355, direction: 2, time: 1000}
                ]

                var roll2 = new Roll(ball2, animations2);
                roll2.setDispach($('.overdue'), ['rollcomplete2']);
                roll2.move();

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

    var module_07 = new Module(800, '.project');
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
            var _self = this;
            $(_self.selector).css('visibility', 'visible');
            $('.animation_02', $(_self.selector)).css('visibility', 'visible');
            $('.animation_02', $(_self.selector)).addClass('bounceIn');
            setTimeout(function(){
                $('.animation_01', $(_self.selector)).css('visibility', 'visible');
                $('.animation_01', $(_self.selector)).addClass('fade-in-left');
            }, 1500);
        }
    };

    var module_03 = new Module(200, '.platform_02');
    module_03.animate = function () {
        if(!$('#platform').hasClass('hidden')) {
            $(this.selector).css('visibility', 'visible');
            var _self = this;

            $('.animation_03', $(_self.selector)).css('visibility', 'visible');
            $('.animation_03', $(_self.selector)).addClass('fade-in-left');

            $('.animation_04', $(_self.selector)).css('visibility', 'visible');
            $('.animation_04', $(_self.selector)).addClass('bounceIn');

            setTimeout(function(){
                $('.animation_05', $(_self.selector)).css('visibility', 'visible');
                $('.animation_05', $(_self.selector)).addClass('fade-in-right');
            }, 1000);

            setTimeout(function() {
                $(_self.selector).checked();
            }, 1800);
        }
    };

    var module_04 = new Module(200, '.platform_03');
    module_04.animate = function () {
        if(!$('#platform').hasClass('hidden')) {
            $(this.selector).css('visibility', 'visible');
            var _self = this;

            $('.animation_07', $(_self.selector)).css('visibility', 'visible');
            $('.animation_07', $(this.selector)).addClass('fade-in-right');

            setTimeout(function(){
                $('.animation_08', $(_self.selector)).css('visibility', 'visible');
                $('.animation_08', $(_self.selector)).addClass('fade-to-small');
            }, 700);

            setTimeout(function() {
                $('.animation_06', $(_self.selector)).css('visibility', 'visible');
                $('.animation_06', $(_self.selector)).addClass('fade-in-left');
            }, 1600);

            setTimeout(function() {
                $(_self.selector).checked();
            }, 2000);


        }
    };

    var module_05 = new Module(200, '.platform_04');
    module_05.animate = function () {
        if(!$('#platform').hasClass('hidden')) {
            $(this.selector).css('visibility', 'visible');
            var _self = this;
            //1. 显示金币
            $('.animation_10', $(_self.selector)).css('visibility', 'visible');
            $('.animation_10', $(_self.selector)).addClass('fade-in');

            //2. 显示盾牌
            setTimeout(function(){
                $('.animation_09', $(_self.selector)).css('visibility', 'visible');
                $('.animation_09', $(_self.selector)).addClass('bounceInDown');
            }, 500);

            //3. 显示文字
            setTimeout(function(){
                $('.animation_11', $(_self.selector)).css('visibility', 'visible');
                $('.animation_11', $(_self.selector)).addClass('fade-in-right');
            }, 1500);

            //4. 显示勾号
            setTimeout(function(){
                $(_self.selector).checked();
            }, 2000);

        }
    };

    var module_06 = new Module(200, '.platform_05');
    module_06.animate = function () {
        if(!$('#platform').hasClass('hidden')) {
            var _self = this;
            //1. 显示图
            $('.animation_13', $(_self.selector)).css('visibility', 'visible');
            $('.animation_13', $(_self.selector)).addClass('fade-to-small');

            //2. 显示文字
            setTimeout(function(){
                $('.animation_12', $(_self.selector)).css('visibility', 'visible');
                $('.animation_12', $(_self.selector)).addClass('fade-in-left');
            }, 800);

            //3. 显示打勾
            setTimeout(function(){
                $(_self.selector).checked();
            }, 1800);

        }
    };

    var module_11 = new Module(200, '.platform_06');
    module_11.animate = function () {
        if(!$('#organization').hasClass('hidden')) {
            var _self = this;
            $('.animation_14', $(_self.selector)).css('visibility', 'visible');
            $('.animation_14', $(_self.selector)).addClass('fadeInUp');

            $('.animation_15', $(_self.selector)).css('visibility', 'visible');
            $('.animation_15', $(_self.selector)).addClass('fadeInUp');

            $('.animation_16', $(_self.selector)).css('visibility', 'visible');
            $('.animation_16', $(_self.selector)).addClass('fadeInUp');

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