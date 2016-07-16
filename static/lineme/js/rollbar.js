/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/6/24
 * Time: 20:04
 */

$(function() {

    var isSafari = Object.prototype.toString.call(window.HTMLElement).indexOf('Constructor') > 0;

    if (!isSafari)
        // Todo: fix select2 in profile
        $('body, .box-body').rollbar({
            scroll: 'vertical',
            sliderOpacity: 0,
            zIndex: 2000,
            blockGlobalScroll: true,
            wheelSpeed: 50,
            touchSpeed: 0.4,
            sliderSize: '25%',
        });
});

