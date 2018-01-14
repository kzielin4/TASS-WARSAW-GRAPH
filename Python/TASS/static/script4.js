$(document).ready(function () {
    $("#list").hide();

    $("#search").click(function () {
        var queryParams = {queryTo: $("#queryTo").val(), queryFrom: $("#queryFrom").val()}
        var searchReq = $.get("/sendRequest", queryParams);
        searchReq.done(function (data) {
            if (data.error) {
                $("#errorMessage").text(data.error);
                $("#successMessage").text("");
                 $("#vehicle").text("");
                $("#tLength").text("");
                $("#path").text("");
                $("#url").attr("href", "");
            }
            else {
                $("#errorMessage").text("");
                $("#successMessage").text(data.success);
                $("#vehicle").text("Środek transportu: " + data.vehicle);
                $("#tLength").text("Czas: " + data.tLength + " [sekund]");
                $("#path").text("Trasa: " + data.path);

                $("#url").attr("href", data.result);
            }
        });
    });

     $("#app-tab").click(function () {
        $("#app").show();
        $("#list").hide();
    });
      $("#list-tab").click(function () {
          $("#list").show();
          $("#app").hide();
    });

})
