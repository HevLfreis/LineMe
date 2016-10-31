/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/8/7
 * Time: 18:59
 */

$(function() {
    var trip = new Trip([
    { header: "Help", content: "Nothing to show.", position: "screen-center"},
    ], {
        showHeader: true,
        showCloseBox: true,
        showNavigation: true,
        tripTheme: "yeti",
        delay: -1
    });

    $("#help").on("click", function () {
        trip.start();
    });
});
