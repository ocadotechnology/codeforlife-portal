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
    userName: string
}

const Navbar: React.FC<User> = ({ userType, userName }) => {


    return (
        <AppBarStyled position="fixed">
            <ToolbarStyled disableGutters>
                <LogoCfl src="/images/navbar/logo_cfl.png" />
                <LogoOcado src="/images/navbar/logo_ocado_group.svg" />
                <NavbarActions userType={userType} userName={userName} />
                {userType === "None" ?
                    <NotLoggedIn />
                    : <UserNameButton userType={userType} userName={userName} />}
                <IconButtonStyled
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