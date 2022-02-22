import React, { useState } from 'react'
import { LinkStyled, ListSingleItem, ListStyled, TypographyHover } from './NavbarStyle'
import { Link, ListItem, ListItemIcon, ListItemText } from '@mui/material'
import { User } from './Navbar'
import RegisterButton from '../Components/Buttons/RegisterButton'
import LogInButton from '../Components/Buttons/LogInButton'
import { Collapse } from '@mui/material'
import { ListItemStyled, ListItemIconStyled } from './NavbarStyle'
import { Typography } from '@mui/material'


import SchoolOutlinedIcon from '@mui/icons-material/SchoolOutlined';
import PersonOutlinedIcon from '@mui/icons-material/PersonOutlined';
import GridViewOutlinedIcon from '@mui/icons-material/GridViewOutlined'
import SportsEsportsOutlinedIcon from '@mui/icons-material/SportsEsportsOutlined'
import ArticleOutlinedIcon from '@mui/icons-material/ArticleOutlined'



const SmallReactiveMenu: React.FC<User> = ({ userType }) => {



    const dynamicContentIcons = [
        <GridViewOutlinedIcon />,
        <SportsEsportsOutlinedIcon />,
        <ArticleOutlinedIcon />
    ]

    const dynamicContent = {
        "Student": {
            "navField": {
                "text": ["Dashboard", "Games", "Scoreboard"],
                "link": ["", "", ""],
            },
            "games": {
                "text": ["Rapid Router"],
                "link": [""],
            },
            "resources": {
                "text": ["Rapid Router"],
                "link": [""],
            }
        },
        "Independent": {
            "navField": {
                "text": ["Dashboard", "Games", "Learning Resources"],
                "link": ["", "", ""],
            },
            "games": {
                "text": ["Rapid Router"],
                "link": [""]
            },
            "resources": {
                "text": ["Rapid Router"],
                "link": [""],
            }
        },
        "Teacher": {
            "navField": {
                "text": ["Dashboard", "Games", "Teaching Resources"],
                "link": ["", "", ""],
            },
            "games": {
                "text": ["Rapid Router", "Kurono"],
                "link": [""],
            },
            "resources": ["Rapid Router", "Kurono"],
            "link": [""]
        },
        "None": {
            "navField": {
                "text": ["Teacher", "Student", "Independent"],
                "link": [""],
            },
            "games": {
                "text": [""],
                "link": [""],
            },
            "resources": {
                "text": [""],
                "link": [""],
            }
        }
    }

    const [menu, setMenu] = useState(false)
    const [games, setGames] = useState(false)
    const [resources, setResources] = useState(false)

    return (
        <ListStyled >
            {userType !== "None" ?
                <ListSingleItem onClick={() => setMenu(!menu)}
                >
                    <ListItemIcon>
                        {userType === "Teacher" ? <PersonOutlinedIcon /> : <SchoolOutlinedIcon />}
                    </ListItemIcon>
                    <TypographyHover variant="subtitle2">{userType}</TypographyHover>
                </ListSingleItem>
                :
                <div>
                    <RegisterButton
                    />
                    <div onClick={() => setMenu(!menu)}>
                        <LogInButton small={true} />
                    </div>
                </div>
            }
            <Collapse in={menu} >

                {dynamicContent[userType].navField.text.map((text, index) => (
                    <div
                    >
                        <ListItemStyled
                            userType={userType}
                            key={text}>
                            <ListItemIconStyled userType={userType}>
                                {dynamicContentIcons[index]}
                            </ListItemIconStyled>
                            {
                                text === "Dashboard" || text === "Scoreboard" ?
                                    <TypographyHover variant="subtitle2">{text}</TypographyHover> :
                                    <div onClick={() => text === "Games" ? setGames(!games) : setResources(!resources)}>
                                        <TypographyHover variant="subtitle2">{text}</TypographyHover>
                                        <Collapse orientation="vertical" in={text === "Games" ? games : resources}>
                                            <ListItemStyled userType={userType}>

                                                {dynamicContent[userType].games.text.map((element: string) => {
                                                    return <Typography onClick={() => console.log(element)} variant="subtitle2">{element}</Typography>
                                                })}
                                            </ListItemStyled>
                                        </Collapse>
                                    </div>
                            }
                        </ListItemStyled>
                    </div>
                ))
                }
            </Collapse >
        </ListStyled >
    )
}

export default SmallReactiveMenu