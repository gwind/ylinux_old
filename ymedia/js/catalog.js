// depends on jQuery library.
// depends on ylinux.js

/*********************************************************************
 * Scripts for the catalog display.
 *   make the catalog display more beautiful and comfortable to read.
 *`
 * Functions whose names ends with "init" indicate that they are for 
 * the element with the ID similar to their name.( without the init part.
 *
 * Created and shared by Wang Zhi.
 *
 **********************************************************************/

/** the Start of the script
 * do some initializations.
 */
$(document).ready(function() {
    topic_item_init();
    catalog_path_init();
});

/** initialize the topic items under element whose ID is "topics-list".
 */
function topic_item_init() {
//     $("#topics-list li>a").click(function(event) {
//         event.preventDefault();
//         ylinux_smooth_load('#view', $(this).attr('href')+' #topic', (function(addr) {
//             return function() {
//                 topic_loaded(addr);
//             };
//         })($(this).attr('href')));
//     });
    $("#topics-list li").css({"list-style":"none", "display":"block"});
    $("#topics-list li").css({"float":"left", "width":"50%", "margin":"0", "padding":"0"});
    pages_act_init();
}

/** The callback function for topics-list.
 * Call this function after the topic loaded. This function mainly construct the strucuture of the element with ID 'topic-view'.
 */
function topic_loaded(addr) {
    load_syntaxhighlighter(); // refer to ylinux.js
    // TODO: an ugly implement of inserting a button.
    $("#view .title").append("<a id=\"back\" style=\"float:right\">[返回]</a>");
    // FIXME: load the posts. To be honest, I think it should be done by the HTML instead of AJAX.
    ylinux_smooth_load("#posts", addr + "ajax_show_posts/");
    $("#back").click(function(event) {
        event.preventDefault();
        ylinux_smooth_load("#view", location.href + " #inner-view", topic_item_init);
    });
}

/** initialize extra function for the element with ID named 'catalog-path'.
 */
function catalog_path_init() {
    $("#catalog-path a").click(function(event) {
        event.preventDefault();
        ylinux_smooth_load("#view", $(this).attr("href") + " #inner-view", topic_item_init);
    });
}

/** initialize the extra function for the element with ID named 'pages-act'.
 */
function pages_act_init() {
    $("#pages-act a").click(function(event) {
        event.preventDefault();
        ylinux_smooth_load("#topics-list", $(this).attr("href") + " #topics-list", topic_item_init);
    });
}
