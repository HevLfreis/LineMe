/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/8/7
 * Time: 18:59
 */

$(function() {
    var trip = new Trip([
    { sel: $("#main-panel"), header: "Global", content: "All members in group are shown here.", position: "e", expose: true},
    {
        sel: $("#info-panel"), header: "Info", content: "" +
        "Static information about the network <br>" +
        "topology of this group is shown here. <br>", position: "w", expose: true
    },
    { sel: $("#normal-mode"), header: "Mode", content: "Switch to map mode.", position: "n"},
    { sel: $(".fa-dot-circle-o"), header: "My Net", content: "Switch to my network.", position: "s"},
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
