import LogInButton from '../Components/Buttons/LogInButton';
import React from 'react'
import RegisterButton from "../Components/Buttons/RegisterButton"
import { User } from "./Navbar"
import { ActionsStyled, ActionsTypographyStyled, NavbarMenuStyled } from './NavbarStyle';

import { Button, Link, Typography } from '@mui/material';
import NavBarDropDown from './NavBarDropDown';
import { LinkStyled } from './NavbarStyle';

export const navbarActions = {
    "Student": {
        "navField": {
            "text": ["Games", "Scoreboard"],
            "link": ["", ""]
        },
        "games": ["Rapid Router", "Kurono"],
        "resources": []
    },
    "Independent": {
        "navField": {
            "text": ["Games", "Learning Resources"],
            "link": ["", ""]
        },
        "games": ["Rapid Router"],
        "resources": ["Rapid Router"]
    },
    "Teacher": {
        "navField": {
            "text": ["Games", "Teaching Resources"],
            "link": ["", ""]
        },
        "games": ["Rapid Router", "Kurono"],
        "resources": ["Rapid Router", "Kurono"],

    },
    "None": {
        "navField": {
            "text": ["Teachers", "Students"],
            "links": ["https://www.codeforlife.education/teach/", "https://www.codeforlife.education/play/"]
        },
        "games": [],
        "resources": []
    },
}



const NavbarActions: React.FC<User> = ({ userType, userName }) => {
    return (
        <ActionsStyled>
            <ActionsTypographyStyled variant="h4" > {userType !== "None" ? userType : null}</ActionsTypographyStyled>
            {userType === "None" ? navbarActions[userType].navField.text.map((element: string, i: number) => {
                return <LinkStyled
                    href={navbarActions[userType].navField.links[i]}
                    variant="h4"
                    color="inherit"
                >{element}</LinkStyled>
            }) :
                <>
                    <ActionsTypographyStyled variant="h6">Dashboard</ActionsTypographyStyled>
                    <NavBarDropDown title="Games" subTitles={navbarActions[userType].games} />
                    {userType === "Student" ? <ActionsTypographyStyled variant="h6" >{navbarActions[userType].navField.text[1]}</ActionsTypographyStyled> :
                        <NavBarDropDown
                            title={navbarActions[userType].navField.text[1]}
                            subTitles={navbarActions[userType].games}
                        />
                    }
                </>
            }
        </ActionsStyled>
    )
}

export default NavbarActions








