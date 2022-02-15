import * as React from 'react';
import Button from '@mui/material/Button';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import { LogInButtonStyled, LogInMenuStyled, MenuItemStyled } from './LogInButtonStyled';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import RegisterButtonStyled from './RegisterButtonStyled';



export const LogInButton: React.FC = () => {

    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);
    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
        console.log(event)
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
        setAnchorEl(null);
    };


    return (
        <div>
            <LogInButtonStyled
                aria-controls={open ? 'basic-menu' : undefined}
                aria-haspopup="true"
                aria-expanded={open ? 'true' : undefined}
                onClick={handleClick}
                endIcon={<KeyboardArrowDownIcon />}
            >
                Log in
            </LogInButtonStyled>
            <LogInMenuStyled
                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
            >
                <MenuItemStyled onClick={handleClose}>Profile</MenuItemStyled>
                <MenuItemStyled onClick={handleClose}>My account</MenuItemStyled>
                <MenuItemStyled onClick={handleClose}>Logout</MenuItemStyled>
            </LogInMenuStyled>
        </div >
    )
}

export default LogInButton
