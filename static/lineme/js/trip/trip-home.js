/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/8/7
 * Time: 18:59
 */

$(function() {
    var trip = new Trip([
    {
        header: "LineMe", content: "" +
        "Welcome to LineMe ~<br><br>" +
        "In LineMe, you can enjoy mapping your friend networks here. <br>" +
        "Create a group, add some friends, everybody creates his own <br>" +
        "net and all nets XXX to a global net.<br><br>" +
        "Are you the center star in you social groups ?<br>" +
        "Let's check it out !!!<br><br>" +
        "Here is the homepage of LineMe, and we will tour you some functions.", position: "screen-center"
    },
    { sel: $(".user-panel"), header: "Avatar", content: "Click avatar to upload yours.", position: "e" },
    { sel: $("#search"), header: "Search", content: "You can search group by name.", position: "e" },
    {
        sel: $("#credits"), header: "Credit", content: "" +
        "Here is your credits in LineMe.<br>" +
        "Credits can be used to create your own group.<br><br>" +
        "A confirmed link will bonus you 10 points.<br>" +
        "A rejected link will also cost you 10 points.<br>", position: "e"
    },
    {
        sel: $("#box-msg"), header: "Request", content: "" +
        "The link requests linking you <br>" +
        "from others will be shown here. <br>" +
        "You can choose to confirm or reject them.", position: "e", expose: true
    },
    {
        sel: $("#box-inv"), header: "Invitation", content: "" +
        "You can check the link invitations <br>" +
        "you have created here.", position: "w", expose: true
    },
    {
        sel: $("#box-group"), header: "Group", content: "" +
        "Here are our recommended groups<br>" +
        "for you, click one to follow.<br><br>" +
        "Also you can check the group you <br>" +
        "have created and joined here.", position: "e", expose: true
    },
    {
        sel: $(".fa-question"), header: "Help", content: "" +
        "When you are confused in LineMe, <br>" +
        "click help to get more infomation.", position: "s"
    },
    { header: "LineMe", content: "Have fun with LineMe ~<br>", position: "screen-center" },
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
