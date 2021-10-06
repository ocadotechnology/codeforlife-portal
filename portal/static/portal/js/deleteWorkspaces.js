function deleteAllLocalStorageWorkspaces(){
    if(localStorage) {
        var query = /(python|blockly)Workspace(Xml){0,1}-([0-9]+)$/;
        var i;
        for (i in localStorage) {
            if (localStorage.hasOwnProperty(i)) {
                var matches = query.exec(i);
                if(matches){
                    localStorage.removeItem(i);
                }
            }
        }
    }
};
