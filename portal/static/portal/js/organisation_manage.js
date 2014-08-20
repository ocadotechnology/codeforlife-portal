function showRemoveConfirmation(path, name) {
    CONFIRMATION_DATA.remove = {
        options: {
            title: 'Remove teacher',
        },
        html: '<p>The teacher "'+name+'", will be removed from the school or club. If they have any classes you will be asked to move them to other teachers of this school or club.</p><p>Are you sure?</p>',
        confirm: function() { window.location.replace(path); },
    };
    openConfirmationBox('remove');
}

function showToggleAdminConfirmation(path, name) {
    CONFIRMATION_DATA.remove = {
        options: {
            title: 'Set administrator permissions',
        },
        html: '<p>The teacher "'+name+'", will be made an administrator of this school or club. They will gain all of the powers that you currently have.</p><p>Are you sure?</p>',
        confirm: function() { window.location.replace(path); },
    };
    openConfirmationBox('remove');
}

function showDisable2FAConfirmation(path, name) {
    CONFIRMATION_DATA.remove = {
        options: {
            title: 'Disable 2FA for '+name,
        },
        html: '<p>The teacher "'+name+'", will have their two factor authentication disabled. This will make their account less secure.</p><p>Are you sure?</p>',
        confirm: function() { window.location.replace(path); },
    };
    openConfirmationBox('remove');
}
