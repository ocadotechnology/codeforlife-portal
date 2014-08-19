function showRemoveConfirmation(path, name) {
    CONFIRMATION_DATA.remove = {
        title: 'Remove teacher',
        html: '<span class="ui-icon ui-icon-alert" style="float:left; margin:0 7px 50px 0;"></span><p>The teacher "'+name+'", will be removed from the school | club. If they have any classes you will be asked to move them to other teachers of this school | club.</p><p>Are you sure?</p>',
        confirm: function() { window.location.replace(path); },
    };
    openConfirmationBox('remove');
}

function showToggleAdminConfirmation(path, name) {
    CONFIRMATION_DATA.remove = {
        title: 'Remove teacher',
        html: '<span class="ui-icon ui-icon-alert" style="float:left; margin:0 7px 50px 0;"></span><p>The teacher "'+name+'", will be made an admin of the school, they will gain all of the powers that you currently have.</p><p>Are you sure?</p>',
        confirm: function() { window.location.replace(path); },
    };
    openConfirmationBox('remove');
}

function showDisable2FAConfirmation(path, name) {
    CONFIRMATION_DATA.remove = {
        title: 'Remove teacher',
        html: '<span class="ui-icon ui-icon-alert" style="float:left; margin:0 7px 50px 0;"></span><p>The teacher "'+name+'", will have their two factor authentication disabled, this will make their account less secure.</p><p>Are you sure?</p>',
        confirm: function() { window.location.replace(path); },
    };
    openConfirmationBox('remove');
}
