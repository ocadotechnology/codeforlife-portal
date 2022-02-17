import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import Button from '@mui/material/Button';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import MailIcon from '@mui/icons-material/Mail';
import Navbar, { User } from './Navbar';

import { MenuIconButtonStyled, SmallMenuBarUserName } from './NavbarStyle';
import MenuIcon from '@mui/icons-material/Menu';

import { navbarActions } from './NavbarActions';

import LoginOutlinedIcon from '@mui/icons-material/LoginOutlined';
import GridViewOutlinedIcon from '@mui/icons-material/GridViewOutlined';
import CookieOutlinedIcon from '@mui/icons-material/CookieOutlined';
import SportsEsportsOutlinedIcon from '@mui/icons-material/SportsEsportsOutlined';
import ArticleOutlinedIcon from '@mui/icons-material/ArticleOutlined';
import Mail from '@mui/icons-material/Mail';
import HelpOutlineOutlinedIcon from '@mui/icons-material/HelpOutlineOutlined';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import PrivacyTipOutlinedIcon from '@mui/icons-material/PrivacyTipOutlined';
import GavelOutlinedIcon from '@mui/icons-material/GavelOutlined';
import LocalLibraryOutlinedIcon from '@mui/icons-material/LocalLibraryOutlined';
import PanToolOutlinedIcon from '@mui/icons-material/PanToolOutlined';
import ManageAccountsOutlinedIcon from '@mui/icons-material/ManageAccountsOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import { Toolbar, Typography } from '@mui/material';
import { LogInButtonStyled } from '../Components/Buttons/LogInButtonStyled';
import RegisterButton from '../Components/Buttons/RegisterButton';
import { RegisterButtonSmallMenuStyled } from '../Components/Buttons/RegisterButtonStyled';

const SmallNavbar: React.FC<User> = ({ userType, userName }) => {

    const dynamicContent = {
        "Student": {
            "navField": {
                "text": ["Games", "Scoreboard"],
                "link": ["", ""],
            },
            "games": {
                "text": ["Rapid Router"],
                "link": [""],
            }
        },
        "Independent": {
            "navField": {
                "text": ["Games", "Learning Resources"],
                "link": ["", ""],
            },
            "games": {
                "text": ["Rapid Router"],
                "link": [""]
            }
        },
        "Teacher": {
            "navField": {
                "text": ["Games", "Scoreboard"],
                "link": ["", ""],
            },
            "games": {
                "text": ["Rapid Router"],
                "link": [""],
            }
        },
        "None": {
            "navField": {
                "text": [],
                "link": [],
            },
            "games": {
                "text": [],
                "link": [],
            }

        }
    }
    const dynamicContentIcons = [
        <SportsEsportsOutlinedIcon />,
        <ArticleOutlinedIcon />
    ]

    const staticContent = [
        "About us",
        "Help and support",
        "Cookie settings",
        "Privacy policy",
        "Terms of use",
        "Home learning",
        "Get involved",
    ]

    const staticContentIcons = [
        <InfoOutlinedIcon />,
        <HelpOutlineOutlinedIcon />,
        <CookieOutlinedIcon />,
        <PrivacyTipOutlinedIcon />,
        <GavelOutlinedIcon />,
        <LocalLibraryOutlinedIcon />,
        <PanToolOutlinedIcon />,
    ]

    const accountContent = [
        "Update account details",
        "Logout"
    ]

    const accountContentIcons = [
        <ManageAccountsOutlinedIcon />,
        <LogoutOutlinedIcon />,
    ]


    const [state, setState] = React.useState({
        bottom: false,
    });

    const toggleDrawer =
        (anchor: any, open: boolean) =>
            (event: React.KeyboardEvent | React.MouseEvent) => {
                if (
                    event.type === 'keydown' &&
                    ((event as React.KeyboardEvent).key === 'Tab' ||
                        (event as React.KeyboardEvent).key === 'Shift')
                ) {
                    return;
                }

                setState({ ...state, [anchor]: open });
            };

    const list = (anchor: any) => (
        <Box
            sx={{ width: anchor === 'bottom' || anchor === 'bottom' ? 'auto' : 'auto' }}
            role="presentation"
            onClick={toggleDrawer(anchor, false)}
            onKeyDown={toggleDrawer(anchor, false)}
        >
            <SmallMenuBarUserName variant="h3">
                {userType !== "None" ? userName : null}
            </SmallMenuBarUserName>
            <List>
                <ListItem>
                    <RegisterButtonSmallMenuStyled />
                </ListItem>
                <ListItem button>
                    <ListItemIcon>{userType !== "None" ? <GridViewOutlinedIcon /> : <LoginOutlinedIcon />}</ListItemIcon>
                    <ListItemText primary={userType !== "None" ? "Dashboard" : "Log in"}></ListItemText>
                </ListItem>
                {dynamicContent[userType].navField.text.map((text, index) => (
                    <ListItem button key={text}>
                        <ListItemIcon>
                            {dynamicContentIcons[index]}
                        </ListItemIcon>
                        <ListItemText primary={text} />
                    </ListItem>
                ))}
            </List>
            <Divider />
            <List>
                {staticContent.map((text, index) => (
                    <ListItem button key={text}>
                        <ListItemIcon>
                            {staticContentIcons[index]}
                        </ListItemIcon>
                        <ListItemText primary={text} />
                    </ListItem>
                ))}
            </List>
            <Divider />
            <List>
                {userType !== "None" ? accountContent.map((text, index) => {
                    return (<ListItem button key={text}>
                        <ListItemIcon>
                            {accountContentIcons[index]}
                        </ListItemIcon>
                        <ListItemText primary={text} />
                    </ListItem>)
                }) : null}
            </List>
        </Box>
    );

    return (
        <div>
            <React.Fragment>
                <MenuIconButtonStyled onClick={toggleDrawer("bottom", true)}
                >{<MenuIcon />}</MenuIconButtonStyled>
                <Drawer
                    anchor={"bottom"}
                    open={state["bottom"]}
                    onClose={toggleDrawer("bottom", false)}
                >
                    {list("bottom")}
                </Drawer>
            </React.Fragment >
        </div >
    );
}
export default SmallNavbar