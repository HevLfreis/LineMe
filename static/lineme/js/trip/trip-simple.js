/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/8/7
 * Time: 18:59
 */

$(function() {
    var trip = new Trip([
    { sel: $(".sidebar-menu"), header: "Group", content: "Click to select group.", position: "e"},
    { sel: $(".fa-globe"), header: "Global", content: "Change to global net.", position: "s"},
    { sel: $(".fa-dot-circle-o"), header: "My", content: "change to my net.", position: "s"},
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
