import React, { useState } from 'react'
import { LinkStyled, ListSingleItem, ListStyled, SubMenuStyled, TypographyHover } from './NavbarStyle'
import { Link, ListItem, ListItemIcon, ListItemText } from '@mui/material'
import { User } from './Navbar'
import RegisterButton from '../Components/Buttons/RegisterButton'
import LogInButton from '../Components/Buttons/LogInButton'
import { Collapse } from '@mui/material'
import { ListItemStyled, ListItemIconStyled } from './NavbarStyle'
import { Typography, Box } from '@mui/material'


import SchoolOutlinedIcon from '@mui/icons-material/SchoolOutlined';
import PersonOutlinedIcon from '@mui/icons-material/PersonOutlined';
import GridViewOutlinedIcon from '@mui/icons-material/GridViewOutlined'
import SportsEsportsOutlinedIcon from '@mui/icons-material/SportsEsportsOutlined'
import ArticleOutlinedIcon from '@mui/icons-material/ArticleOutlined'


interface StringBoolHash {
    [variable: string]: boolean
}

const SmallReactiveMenu: React.FC<User> = ({ userType }) => {

    const isGame = (text: string) => {
        return text === "Games" ? "games" : "resources"
    }
    // Strings that are not considered for dropdown menu

    const NotDropDown: StringBoolHash = {
        "Dashboard": true,
        "Scoreboard": true,
        "Teacher": true,
        "Student": true,
        "Independent": true
    }

    const dynamicContentIcons = [
        <GridViewOutlinedIcon />,
        <SportsEsportsOutlinedIcon />,
        <ArticleOutlinedIcon />
    ]
    interface ContentTemplate {
        Student: {
            navField: {
                text: string[],
                link: string[]
            },
            games: {
                text: string[],
                link: string[]
            },
            resources: {
                text: string[],
                link: string[]
            }
        },
        Independent: {
            navField: {
                text: string[],
                link: string[]
            },
            games: {
                text: string[],
                link: string[]
            },
            resources: {
                text: string[],
                link: string[]
            }
        },
        Teacher: {

            navField: {
                text: string[],
                link: string[]
            },
            games: {
                text: string[],
                link: string[]
            },
            resources: {
                text: string[],
                link: string[]
            }
        },
        None: {
            navField: {
                text: string[],
                link: string[]
            },
            games: {
                text: string[],
                link: string[]
            },
            resources: {
                text: string[],
                link: string[]
            }
        }
    }

    const dynamicContent: ContentTemplate = {
        "Student": {
            "navField": {
                "text": ["Dashboard", "Games", "Scoreboard"],
                "link": ["https://www.codeforlife.education/teach/dashboard/#school", "", ""],
            },
            "games": {
                "text": ["Rapid Router"],
                "link": ["https://www.codeforlife.education/rapidrouter/"],
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
                "text": ["Rapid Router"],
                "link": ["https://www.codeforlife.education/rapidrouter/"],
            },
            "resources": {
                "text": ["Rapid Router", "Kurono"],
                "link": ["", ""]
            }
        },
        "None": {
            "navField": {
                "text": ["Teacher", "Student", "Independent"],
                "link": [
                    "https://www.codeforlife.education/login/teacher/",
                    "https://www.codeforlife.education/login/student/",
                    "https://www.codeforlife.education/login/independent/"
                ],
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
                    <Typography variant="subtitle2">{userType}</Typography>
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

                <Box
                >
                    {dynamicContent[userType].navField.text.map((text, index) => (
                        <ListItemStyled
                            userType={userType}
                            key={text}>
                            <ListItemIconStyled userType={userType}>
                                {dynamicContentIcons[index]}
                            </ListItemIconStyled>
                            {
                                // Dashboard and Scoreboard never have dropdown buttons
                                NotDropDown[text] ?
                                    <LinkStyled href={userType === "None" ? dynamicContent[userType].navField.text[index] : ""} userType={userType} variant="subtitle2">{text}</LinkStyled> :
                                    // Alter between games and resources
                                    <div onClick={() => text === "Games" ? setGames(!games) : setResources(!resources)}>
                                        <LinkStyled userType={userType} variant="subtitle2">{text}</LinkStyled>
                                        <Collapse orientation="vertical" in={text === "Games" ? games : resources}>
                                            <SubMenuStyled userType={userType}>

                                                {dynamicContent[userType][isGame(text)].text.map((element: string, index: number) => {
                                                    return (
                                                        <LinkStyled
                                                            href={dynamicContent[userType][isGame(text)].link[index]}
                                                            userType={userType}
                                                            variant="subtitle2">
                                                            {element}
                                                        </LinkStyled>
                                                    )
                                                })}
                                            </SubMenuStyled>
                                        </Collapse>
                                    </div>
                            }
                        </ListItemStyled>
                    ))
                    }
                </Box>

            </Collapse >
        </ListStyled >
    )
}

export default SmallReactiveMenu