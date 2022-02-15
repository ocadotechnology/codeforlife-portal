import LogInButton from '../Components/Buttons/LogInButton';
import React from 'react'
import RegisterButton from "../Components/Buttons/RegisterButton"
import { User } from "./Navbar"
import { ActionsStyled, ActionsTypographyStyled } from './NavbarStyle';



interface Actions {
    Student: {
        navField: string[]
        games: string[]
    }
    Independent: {
        navField: string[]
        games: string[]
    },

    Teacher: {
        navField: string[]
        games: string[]
    }

    None: {
        navField: string[]
    }
}

const navbarActions: Actions = {
    "Student": {
        "navField": ["Dashboard", "Games", "Scoreboard"],
        "games": ["Rapid Router"]
    },
    "Independent": {
        "navField": ["Dashboard", "Games", "Learning Resources"],
        "games": ["Rapid Router"]
    },
    "Teacher": {
        "navField": ["Dashboard", "Games", "Teaching Resources"],
        "games": ["Rapid Router", "Kurono"],
    },
    "None": { "navField": ["Teachers", "Students"] },
}



const NavbarActions: React.FC<User> = ({ userType, userName }) => {
    return (
        <ActionsStyled>
            <ActionsTypographyStyled variant="h4" > {userType !== "None" ? userType : null}</ActionsTypographyStyled>
            {
                navbarActions[userType].navField.map(element => {
                    return <ActionsTypographyStyled
                        variant="h6">{element}</ActionsTypographyStyled>
                })
            }
        </ActionsStyled>
    )
}

export default NavbarActions








