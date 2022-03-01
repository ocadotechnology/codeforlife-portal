import React from "react";
import { NavBarButtonStyled, NavButtonItemStyled } from "./NavbarStyle";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import { NavbarMenuStyled } from "./NavbarStyle";

interface Props {
    title: string;
    subTitles: string[];
}

const NavBarDropDown = ({ title, subTitles }: Props) => {
    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);
    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
        console.log(event);
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
        setAnchorEl(null);
    };

    return (
        <div>
            <NavBarButtonStyled
                aria-controls={open ? "basic-menu" : undefined}
                aria-haspopup="true"
                aria-expanded={open ? "true" : undefined}
                onClick={handleClick}
                endIcon={<KeyboardArrowDownIcon />}
            >
                {title}
            </NavBarButtonStyled>
            <NavbarMenuStyled anchorEl={anchorEl} open={open} onClose={handleClose}>
                {subTitles.map((element: string, i: number) => {
                    return (
                        <NavButtonItemStyled onClick={handleClose}>
                            {element}
                        </NavButtonItemStyled>
                    );
                })}
            </NavbarMenuStyled>
        </div>
    );
};

export default NavBarDropDown;
