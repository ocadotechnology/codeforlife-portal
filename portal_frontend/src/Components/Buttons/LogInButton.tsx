import * as React from 'react';
import { useState, useEffect } from 'react';
import Button from '@mui/material/Button';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import { LogInButtonStyled, LogInMenuStyled, MenuItemStyled, SubButtonStyled } from './LogInButtonStyled';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import RegisterButtonStyled from './RegisterButtonStyled';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';


export const LogInButton: React.FC = () => {

    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);
    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
        console.log(event)
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
        setAnchorEl(null);
    };

    // Bug where the open dropdown follows
    // window resize, so close it on resize

    useEffect(() => {
        const handleResize = () => {
            handleClose()
        }
        window.addEventListener('resize', handleResize)
    })

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
                <SubButtonStyled onClick={handleClose}>Teacher <ChevronRightIcon /></SubButtonStyled>
                <SubButtonStyled onClick={handleClose}>Student <ChevronRightIcon /></SubButtonStyled>
                <SubButtonStyled onClick={handleClose}>Independent <ChevronRightIcon /></SubButtonStyled>
            </LogInMenuStyled>
        </div >
    )
}

export default LogInButton
