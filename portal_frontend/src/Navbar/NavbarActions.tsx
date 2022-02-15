import LogInButton from '../Components/Buttons/LogInButton';
import React from 'react'
import RegisterButton from "../Components/Buttons/RegisterButton"
import { User } from "./Navbar"
import { ActionsStyled, ActionsTypographyStyled, NavbarMenuStyled } from './NavbarStyle';

import { Button, Typography } from '@mui/material';
import NavBarDropDown from './NavBarDropDown';

const navbarActions = {
    "Student": {
        "navField": ["Games", "Scoreboard"],
        "games": ["Rapid Router", "Kurono"],
        "resources": []
    },
    "Independent": {
        "navField": ["Games", "Learning Resources"],
        "games": ["Rapid Router"],
        "resources": ["Rapid Router"]
    },
    "Teacher": {
        "navField": ["Games", "Teaching Resources"],
        "games": ["Rapid Router", "Kurono"],
        "resources": ["Rapid Router", "Kurono"],

    },
    "None": {
        "navField": ["Teachers", "Students"],
        "games": [],
        "resources": []
    },
}



const NavbarActions: React.FC<User> = ({ userType, userName }) => {
    return (
        <ActionsStyled>
            <ActionsTypographyStyled variant="h4" > {userType !== "None" ? userType : null}</ActionsTypographyStyled>
            {userType === "None" ? navbarActions[userType].navField.map(element => {
                return <ActionsTypographyStyled variant="h6">{element}</ActionsTypographyStyled>
            }) :
                <>
                    <ActionsTypographyStyled variant="h6">Dashboard</ActionsTypographyStyled>
                    <NavBarDropDown title="Games" subTitles={navbarActions[userType].games} />
                    {userType === "Student" ? <ActionsTypographyStyled variant="h6" >{navbarActions[userType].navField[1]}</ActionsTypographyStyled> :
                        <NavBarDropDown
                            title={navbarActions[userType].navField[1]}
                            subTitles={navbarActions[userType].games}
                        />
                    }
                </>
            }
        </ActionsStyled>
    )
}

export default NavbarActions








