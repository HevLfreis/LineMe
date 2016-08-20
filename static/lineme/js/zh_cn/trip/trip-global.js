/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/8/7
 * Time: 18:59
 */

$(function() {
    var trip = new Trip([
    { sel: $("#main-panel"), header: "全局", content: "所有成员都在这里", position: "e", expose: true },
    { sel: $("#info-panel"), header: "信息", content: "网络的一些有趣的拓扑信息<br>", position: "w", expose: true },
    { sel: $("#normal-mode"), header: "模式", content: "切换到地图", position: "n" },
    { sel: $(".fa-dot-circle-o"), header: "我的", content: "切换到我的网络", position: "s" },
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
