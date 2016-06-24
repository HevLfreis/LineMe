/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/4/15
 * Time: 9:05
 */
var emails = "{{ human.email }}".split("@");
var births = "{{ human.birth }}".split(",");
var locations = "{{ human.location }}".split(" ");
var institutions = "{{ human.institution }}".split(" ");
$('#profile-email1').text(emails[0]);
$('#profile-email2').text('@'+emails[1]);
$('#profile-birth').text(births[0]);
$('#profile-location1').text(locations[0]);
$('#profile-location2').text(locations[1]);
$('#profile-institution1').text(institutions[0]);
$('#profile-institution2').text(institutions[1]);
