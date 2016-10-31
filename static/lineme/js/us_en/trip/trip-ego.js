/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/8/7
 * Time: 18:59
 */

$(function() {
    var trip1 = new Trip([
    { sel: $("#main-panel"), header: "Mapping", content: "Map your friend network here.", position: "e", expose: true },
    { sel: $("#rcmd-panel"), header: "Member", content: "Click to add him/her to your network.<br>" , position: "w", expose: true },
    {
        sel: $(".bt-menu-trigger"), header: "Tool", content: "" +
        "Click to expand the tool bar. <br>" +
        "For more about network oprations, <br>" +
        "please click tool -> Howto", position: "n"
    },
    {
        sel: $("#search"), header: "Search", content: "" +
        "You can also search and add <br>" +
        "a member by his/her name.", position: "e"
    },
    { sel: $(".fa-globe"), header: "Global Net", content: "Switch to global network.", position: "s" },
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
        "<strong>Add Node</strong> : Click right or search on left<br>" +
        "<strong>Link</strong> : Click one, click another<br>" +
        "<strong>Delete Node</strong> : Double click, " +
        "<strong>Delete Link</strong> : Click it<br><br>" +
        //"</div>" +
        "Tool Bar<br><br>" +
        "<strong>LineMe</strong> : Link all nodes to me<br> " +
        "<strong>Clear</strong> : Clear all links<br>" +
        "<strong>Save</strong> : Save the network, " +
        "<strong>Reset</strong> : Reset the network<br>" +
        "<strong>Info</strong> : Info about the network , " +
        "<strong>Howto</strong> : Show help<br><br>" +
        "Legend<br><br>" +
        '<svg height="10" width="50" style="padding-top:5px"><line x1="0" y1="0" x2="50" y2="0" style="stroke:#38363a;stroke-opacity: 0.1;stroke-width:5;" /></svg> : Unconfirmed link<br>' +
        '<svg height="10" width="50" style="padding-top:5px"><line x1="0" y1="0" x2="50" y2="0" style="stroke:#38363a;stroke-opacity: 0.5;stroke-width:5;" /></svg> : Confirmed link<br>' +
        '<svg height="10" width="50" style="padding-top:5px"><line x1="0" y1="0" x2="50" y2="0" style="stroke:#572dcd;stroke-width:5;" /></svg> : New link<br>' +
        '<svg height="10" width="50" style="padding-top:5px"><line x1="0" y1="0" x2="50" y2="0" style="stroke:#cd0500;stroke-width:5;" /></svg> : Rejected link<br>' +
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
