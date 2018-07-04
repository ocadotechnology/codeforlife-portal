    var fileReader, theText = document.getElementById("form-create-students").elements.item(1);

    function activateImport(){
        $("#studentNamesFileImport").click();
    }

    function writeStudents(){
        fileReader = new FileReader();
        fileReader.readAsText(document.getElementById("studentNamesFileImport").files[0]);
        fileReader.addEventListener("loadend", showNames);
    }

    function showNames(){
        var names = fileReader.result;
        names = names.split(",").join("\n");
        theText.value+=names;
    }
