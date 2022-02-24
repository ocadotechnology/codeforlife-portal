import * as React from 'react';
import { useState, useEffect } from 'react';
import { LogInButtonStyled, LogInMenuStyled, MenuItemStyled, SubButtonStyled } from './NavbarStyle';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

interface Small {
    small?: Boolean
}

export const LogInButton: React.FC<Small> = ({ small }) => {

    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
        setAnchorEl(event.currentTarget);
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
            {small ? null :
                <LogInMenuStyled
                    anchorEl={anchorEl}
                    open={open}
                    onClose={handleClose}
                >
                    <SubButtonStyled onClick={handleClose}>Teacher <ChevronRightIcon /></SubButtonStyled>
                    <SubButtonStyled onClick={handleClose}>Student <ChevronRightIcon /></SubButtonStyled>
                    <SubButtonStyled onClick={handleClose}>Independent <ChevronRightIcon /></SubButtonStyled>
                </LogInMenuStyled>
            }
        </div>
    )
}

export default LogInButton
