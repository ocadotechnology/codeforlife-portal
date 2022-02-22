import { useState } from "react";
import RegisterButton from '../Components/Buttons/RegisterButton';
import LogInButton from '../Components/Buttons/LogInButton';
import * as React from 'react';

import { IconButtonStyled, AppBarStyled, ToolbarStyled, LogoCfl, LogoOcado } from "./NavbarStyle"
import NavbarActions from './NavbarActions';
import UserNameButton from "../Components/Buttons/UserNameButton"
import NotLoggedIn from '../Components/Buttons/NotLoggedIn';
import SmallNavbar from "./SmallNavbar";


export type UserType = "Student" | "Independent" | "Teacher" | "None";

export interface User {
    userType: UserType
    userName?: string
}

const Navbar: React.FC<User> = ({ userType, userName }) => {


    return (
        <AppBarStyled position="fixed">
            <ToolbarStyled disableGutters>
                <a href="http://www.localhost:3000">
                    <LogoCfl src="/images/navbar/logo_cfl.png" />
                </a>
                <a
                    href="https://www.ocadogroup.com/our-responsible-business/corporate-responsibility/skills-for-the-future"
                    target="_blank"
                >
                    <LogoOcado src="/images/navbar/logo_ocado_group.svg" />
                </a>
                <NavbarActions userType={userType} userName={userName} />
                {userType === "None" ?
                    <NotLoggedIn />
                    : <UserNameButton userType={userType} userName={userName} />}
                <IconButtonStyled disableRipple={true}
                    size="large"
                    aria-label="account of current user"
                    aria-controls="menu-appbar"
                    aria-haspopup="true"
                    color="inherit"
                >
                    <SmallNavbar userType={userType} userName={userName} />
                </IconButtonStyled>
            </ToolbarStyled>
        </AppBarStyled>
    );
};
export default Navbar;