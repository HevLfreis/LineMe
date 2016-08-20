/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/8/7
 * Time: 18:59
 */

$(function() {
    var trip1 = new Trip([
    { sel: $("#main-panel"), header: "构建", content: "在这里构建朋友网络", position: "e", expose: true },
    { sel: $("#rcmd-panel"), header: "成员", content: "点击将朋友添加到你的网络中 <br>", position: "w", expose: true },
    {
        sel: $(".bt-menu-trigger"), header: "工具", content: "" +
        "点击展开工具栏 <br>" +
        "更多操作请点击工具中的帮助<br>" , position: "n"
    },
    {
        sel: $("#search"), header: "搜索", content: "" +
        "你可以搜索某个成员来 <br>" +
        "把他加到朋友网络中", position: "e"
    },
    { sel: $(".fa-globe"), header: "全局", content: "切换到全局网络", position: "s" },
    ], {
        showHeader: true,
        showCloseBox: true,
        showNavigation: true,
        tripTheme: "yeti",
        delay: -1
    });

    $("#help").on("click", function () {
        trip1.start();
    });

    var trip2 = new Trip([
    {
        header: "帮助", content: "<div style='font-size: 20px'>" +
        "基础操作<br><br>" +
        //"<div style='text-align: left'>" +
        "<strong>添加</strong> : 点击右侧推荐或者在搜索框搜索<br>" +
        "<strong>连接</strong> : 点击朋友，再点击另一个<br>" +
        "<strong>删除点</strong> : 双击 ，" +
        "<strong>删除边</strong> : 点击<br><br>" +
        //"</div>" +
        "工具栏<br><br>" +
        "<strong>连我</strong> : 所有朋友连到我<br> " +
        "<strong>清除</strong> : 清除所有连边<br>" +
        "<strong>保存</strong> : 保存网络 , " +
        "<strong>重置</strong> : 重置到刚载入状态<br>" +
        "<strong>信息</strong> : 网络的一些信息  , " +
        "<strong>帮助</strong> : 打开帮助<br><br>" +
        "图例<br><br>" +
        '<svg height="10" width="50" style="padding-top:5px"><line x1="0" y1="0" x2="50" y2="0" style="stroke:#38363a;stroke-opacity: 0.1;stroke-width:5;" /></svg> : 未确认<br>' +
        '<svg height="10" width="50" style="padding-top:5px"><line x1="0" y1="0" x2="50" y2="0" style="stroke:#38363a;stroke-opacity: 0.5;stroke-width:5;" /></svg> : 已确认<br>' +
        '<svg height="10" width="50" style="padding-top:5px"><line x1="0" y1="0" x2="50" y2="0" style="stroke:#572dcd;stroke-width:5;" /></svg> : 新添加<br>' +
        '<svg height="10" width="50" style="padding-top:5px"><line x1="0" y1="0" x2="50" y2="0" style="stroke:#cd0500;stroke-width:5;" /></svg> : 已拒绝<br>' +
        '</div><br>',
        position: "screen-center"
    },
    ], {
        prevLabel: null,
        finishLabel: null,
        showCloseBox: true,
        showNavigation: true,
        tripTheme: "white",
        delay: -1
    });

    $("#howto").on("click", function () {
        resetMenu();
        trip2.start();
    });
});
