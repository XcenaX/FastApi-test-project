document.addEventListener('DOMContentLoaded', function(){
    $("#predict_input").change(function(e) {
        var file = e.target.files[0];
        var formData = new FormData();
        formData.append('file', file, file.name);
        //var formData = new FormData($("#main_file_form")[0])
        $.ajax({
            type: "POST",
            url: "/predict",
            // data: JSON.stringify({
            //     "file": file
            // }),
            data: formData,
            // headers: {
            //     "Content-Type": "multipart/form-data"
            // },
            success: function (result) {
               console.log(result);
               data = result["predictions"];
               predictions = "";
               for(var i = 0; i < data.length; i++){
                    predictions += data[i] + "\n";
               }
               $("#predictions")[0].textContent = predictions;
            },
            error: (jQxhr, textStatus, errorThrown) => {
                console.log(textStatus, errorThrown, jQxhr)
            },
            crossDomain: true,            
            processData: false,
            contentType: false,
            enctype: 'multipart/form-data',
        });
    });
});