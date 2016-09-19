/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/8/7
 * Time: 18:59
 */

$(function() {
    var trip = new Trip([
    {
        header: "LineMe", content: "" +
        "欢迎来到 LineMe ~<br><br>" +
        "在 LineMe, 你可以自由地构建自己的朋友网络 <br>" +
        "创建群，添加一些成员，每个人都描绘自己的朋友圈 <br>" +
        "所有的信息汇总起来就是一个庞大的全局网络<br><br>" +
        "你是不是其中的明星呢?<br><br>" +
        "这里是 LineMe 的主页，下面会向你介绍一些简单的功能", position: "screen-center"
    },
    { sel: $(".user-panel"), header: "头像", content: "点击上传你的头像", position: "e" },
    { sel: $("#search"), header: "搜索", content: "搜索群的名字", position: "e" },
    {
        sel: $("#credits"), header: "积分", content: "" +
        "这里是你在 LineMe 的积分<br>" +
        "积分可以用来创建组<br><br>" +
        "当你创建了一条有效连边，你会被奖励<br>" +
        "当你的连边被你的朋友都拒绝了话，你会被惩罚<br>", position: "e"
    },
    {
        sel: $("#box-msg"), header: "请求", content: "" +
        "其他人的连边请求都在这里<br>" +
        "你可以选择确定或者拒绝", position: "e", expose: true
    },
    { sel: $("#box-inv"), header: "邀请", content: "这里是你创建的连边请求 <br>", position: "w", expose: true },
    {
        sel: $("#box-group"), header: "群", content: "" +
        "这里是我们根据你的注册向你推荐的群<br>" +
        "你也可以查看自己创建的群和加入的群<br>", position: "e", expose: true
    },
    {
        sel: $(".fa-question"), header: "帮助", content: "" +
        "当你搞不定 LineMe 的时候, <br>" +
        "每个页面都会有帮助来帮助你！", position: "s"
    },
    { header: "LineMe", content: "玩的愉快（捂脸逃） ~<br>", position: "screen-center" },
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

    if (first === 'True') trip.start();
});
