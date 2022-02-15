import React from 'react'
import { UserNameButtonStyled } from './UserNameButtonStyled'
import PersonOutlineIcon from '@mui/icons-material/PersonOutline';
import { UserItemStyled, UserButtonDivStyled } from './LogInButtonStyled';
import { UserMenuStyled } from './UserNameButtonStyled';

import LogoutIcon from '@mui/icons-material/Logout';
import ManageAccountsIcon from '@mui/icons-material/ManageAccounts';

import { User, UserType } from '../../Navbar/Navbar';
import LogInButton from './LogInButton';
import { OverridableComponent } from '@mui/material/OverridableComponent';
import { SvgIconTypeMap } from '@mui/material';

interface Settings {
    Student: {
        navFieldText: string[]
        navFieldURLs: string[]
        navFieldIcons: JSX.Element[]
    }
    Independent: {
        navFieldText: string[]
        navFieldURLs: string[]
        navFieldIcons: JSX.Element[]
    },

    Teacher: {
        navFieldText: string[]
        navFieldURLs: string[]
        navFieldIcons: JSX.Element[]
    }
}

const logInSettings: Settings = {
    "Student": {
        "navFieldText": ["Log out", "Change Password"],
        "navFieldURLs": ["", ""],
        "navFieldIcons": [],
    },
    "Independent": {
        "navFieldText": ["Log out", "Update account details"],
        "navFieldURLs": ["", ""],
        "navFieldIcons": [],
    },
    "Teacher": {
        "navFieldText": ["Log out", "Update account details"],
        "navFieldURLs": ["", ""],
        "navFieldIcons": [<LogoutIcon />, <ManageAccountsIcon />],
    }
}


const UserNameButton: React.FC<User> = ({ userType, userName }) => {
    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);
    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
        console.log(event)
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
        setAnchorEl(null);
    };

    const user = String(userType)
    return (
        <UserButtonDivStyled>

            <UserNameButtonStyled
                endIcon={<PersonOutlineIcon />}

                aria-controls={open ? 'basic-menu' : undefined}
                aria-haspopup="true"
                aria-expanded={open ? 'true' : undefined}
                onClick={handleClick}
            >
                {userName}
            </UserNameButtonStyled>
            <UserMenuStyled

                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
            >
                {
                    logInSettings[userType].navFieldText.map((element: string, i: number) => {
                        return (
                            <div>
                                <UserItemStyled
                                    onClick={handleClose}
                                    endIcon={logInSettings[user].navFieldIcons[i]}
                                    href={logInSettings[user].navField}
                                >{element}</UserItemStyled>
                            </div>

                        )
                    })
                }
            </UserMenuStyled >
        </UserButtonDivStyled>
    )
}

export default UserNameButton