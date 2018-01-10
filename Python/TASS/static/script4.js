$(document).ready(function () {
    $("#search").click(function () {
        var queryParams = {queryTo: $("#queryTo").val(), queryFrom: $("#queryFrom").val()}
        var searchReq = $.get("/sendRequest", queryParams);
        searchReq.done(function (data) {
            if (data.error) {
                $("#errorMessage").text(data.error)
                $("#url").attr("href", "");
            }
            else {
                $("#errorMessage").text("");
                $("#url").attr("href", data.result);
            }
        });
    });

})
