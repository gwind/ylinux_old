function ajax_list_catalog (url) {
    $("#wiki-container-main").load(url, function () {
        $(this).addClass("list-catalog-done");
    });
}