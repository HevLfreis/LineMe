/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/8/7
 * Time: 18:59
 */

$(function() {
    var trip1 = new Trip([
    { sel: $("#main-panel"), header: "Mapping", content: "Map your friend network here.", position: "e", expose: true},
    {
        sel: $(".bt-menu-trigger"), header: "Tool", content: "" +
        "Click to expand the tool bar. <br>" +
        "For more about network oprations, <br>" +
        "please click tool -> Howto", position: "n"
    },
    {
        sel: $("#rcmd-panel"), header: "Member", content: "" +
        "Recommended members in group are shown <br>" +
        "here. Click to add him/her to your network.", position: "w", expose: true
    },
    {
        sel: $("#search"), header: "Search", content: "" +
        "You can also search and add <br>" +
        "a member by his/her name.", position: "e"
    },
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
        header: "Network Operations", content: "<div style='font-size: 20px'>" +
        "Basic Operations<br><br>" +
        //"<div style='text-align: left'>" +
        "<strong>Add Node</strong> : click right or search on left<br>" +
        "<strong>Link</strong> : click one, click another<br>" +
        "<strong>Delete Node</strong> : double click, " +
        "<strong>Delete Link</strong> : click it<br><br>" +
        //"</div>" +
        "Tool Bar<br><br>" +
        "<strong>LineMe</strong> : link all nodes to me<br> " +
        "<strong>Save</strong> : save the network<br>" +
        "<strong>Reset</strong> : reset the network , " +
        "<strong>Clear</strong> : clear all links<br>" +
        "<strong>Info</strong> : info about the network , " +
        "<strong>Howto</strong> : show help<br><br>" +
        "Legend<br><br>" +
        '<svg height="10" width="50" style="padding-top:5px"><line x1="0" y1="0" x2="50" y2="0" style="stroke:#38363a;stroke-opacity: 0.1;stroke-width:5;" /></svg> : unconfirmed link<br>' +
        '<svg height="10" width="50" style="padding-top:5px"><line x1="0" y1="0" x2="50" y2="0" style="stroke:#38363a;stroke-opacity: 0.5;stroke-width:5;" /></svg> : confirmed link<br>' +
        '<svg height="10" width="50" style="padding-top:5px"><line x1="0" y1="0" x2="50" y2="0" style="stroke:#572dcd;stroke-width:5;" /></svg> : new link<br>' +
        '<svg height="10" width="50" style="padding-top:5px"><line x1="0" y1="0" x2="50" y2="0" style="stroke:#cd0500;stroke-width:5;" /></svg> : rejected link<br>' +
        '</div>',
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
