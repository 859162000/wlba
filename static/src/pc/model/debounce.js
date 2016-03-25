


define(function ($) {
    var debounce = function (fn, delay){
        var timer = null;
        return function () {
            var
              context = this,
              args = arguments;
            clearTimeout(timer);

            timer = setTimeout(function () {
                fn.apply(context, args);
            }, delay);
        };
    }

    return debounce
});