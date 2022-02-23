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
            "text": ["Dashboard", "Games", "Scoreboard"],
            "link": ["", "", ""]
        },
        "games": {
            "text":
                ["Dashboard", "Rapid Router", "Kurono"],
            "link": ["", "", ""]
        },
        "resources": {
            "text": [""],
            "link": [""],
        },
    },
    "Independent": {
        "navField": {
            "text": ["Games", "Learning Resources"],
            "link": ["", ""]
        },
        "games": {
            "text":
                ["Rapid Router"],
            "link": [""]
        },
        "resources": {
            "text":
                ["Rapid Router"],
            "link": [""]
        }
    },
    "Teacher": {
        "navField": {
            "text": ["Games", "Teaching Resources"],
            "link": ["", ""]
        },
        "games": {
            "text":
                ["Rapid Router", "Kurono"],
            "link": [""]
        },
        "resources": {
            "text":
                ["Rapid Router", "Kurono"],
            "link": [""]
        },

    },
    "None": {
        "navField": {
            "text": ["Teachers", "Students"],
            "links": ["https://www.codeforlife.education/teach/", "https://www.codeforlife.education/play/"]
        },
        "games": {
            "text":
                [""],
            "link": [""]
        },
        "resources": {
            "text": [""],
            "link": [""]
        }
    },
}

interface StringBoolHash {
    [key: string]: boolean
}

const NotDropDown: StringBoolHash = {
    "Dashboard": true,
    "Scoreboard": true,
}

const isGame = (text: string) => {
    return text === "Games" ? "games" : "resources"
}

// TODO: Make this component resemble the mobile version
const NavbarActions: React.FC<User> = ({ userType, userName }) => {
    return (
        <ActionsStyled>
            <ActionsTypographyStyled variant="h4" > {userType !== "None" ? userType : null}</ActionsTypographyStyled>
            {userType === "None" ? navbarActions[userType].navField.text.map((element: string, i: number) => {
                return <LinkStyled userType={userType}
                    href={navbarActions[userType].navField.links[i]}
                    variant="h4"
                >{element}</LinkStyled>
            }) :
                <>
                    {navbarActions[userType].navField.text.map((element: string, index: number) => {
                        return NotDropDown[element] ? <LinkStyled userType={userType}>{element}</LinkStyled> :
                            <NavBarDropDown title={element} subTitles={navbarActions[userType][isGame(element)].text} />
                    })
                    }
                </>
            }
        </ActionsStyled>
    )
}

export default NavbarActions








