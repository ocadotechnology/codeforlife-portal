import {
    MenuItem,
    Menu,
    Button,
    Box,
    AppBar,
    Toolbar,
    IconButton,
    Typography,
    Link,
    Drawer,
    List,
    ListItem,
    ListItemIcon
} from '@mui/material';
import React from 'react';
import { styled } from "@mui/material/styles"
import { User, UserType } from "./Navbar"
import { useState } from 'react';
import { OverridableStringUnion } from "@mui/types/index"
import { TypographyPropsVariantOverrides } from "@mui/material/Typography"
import { Variant } from '@mui/material/styles/createTypography';

export const AppBarStyled = styled(AppBar)(({ theme }) => ({
    zIndex: "1201",
    background: "white",
    color: "black",
    padding: "0px 0px 0px 1rem"
}))

export const ToolbarStyled = styled(Toolbar)(({ theme }) => ({
    display: "flex",
    flexDirection: "row",
    [theme.breakpoints.up("lg")]: {
        height: "100px",
        justifyContent: "start"
    },
    [theme.breakpoints.down("lg")]: {
        height: "80px",
        justifyContent: 'space-between',
    },
    [theme.breakpoints.down("md")]: {
        height: "65px",
        justifyContent: 'space-between',
    },
    "& > button": {
        [theme.breakpoints.up("lg")]: {
            marginLeft: "auto"
        }
    }
}))

export const LogoCfl = styled("img")(({ theme }) => ({
    [theme.breakpoints.up("lg")]: {
        height: "70px"
    },
    [theme.breakpoints.only("md")]: {
        height: "70px"
    },
    [theme.breakpoints.down("md")]: {
        height: "50px"
    },
}))

export const LogoOcado = styled("img")(({ theme }) => ({
    [theme.breakpoints.up("lg")]: {
        height: "52px",
        marginLeft: "4rem"
    }
}))

export const IconButtonStyled = styled(IconButton)(({ theme }) => ({
    [theme.breakpoints.up("lg")]: {
        display: "none",
    },
    "&:hover": {
        background: "none"
    }
}))

export const ActionsStyled = styled("div")(({ theme }) => ({
    display: "flex",
    alignItems: "center",
    flexDirection: "row",
    [theme.breakpoints.down("lg")]: {
        display: "none",
    }
}))

export const ActionsTypographyStyled = styled(Typography)(({ theme }) => ({
    margin: "2rem",
}))

export const NavBarButtonStyled = styled(Button)(({ theme }) => ({
    color: "black",
    textTransform: "none",
    fontWeight: "500",
    "&:hover": {
        background: "none",
        textDecoration: "underline",
    }
}))

export const NavButtonItemStyled = styled(MenuItem)(({ theme }) => ({
    "&:hover": {
        background: "none",
        textDecoration: "underline",
    }
}))
export const NavbarMenuStyled = styled(Menu)(({ theme }) => ({
    "& > div > ul": {
        paddingTop: "0",
        paddingBottom: "0",
        paddingLeft: "1rem",
        paddingRight: "3rem"
    }
}))


interface LinkAttr {
    variant?: OverridableStringUnion<Variant | 'inherit', TypographyPropsVariantOverrides>,
    href?: string,
    userType: UserType,
}

export const LinkStyled: React.FC<LinkAttr> = (props) => {

    return (
        <Link
            href={props.href}
            variant={props.variant}
            sx={{
                marginRight: "2rem",
                textDecoration: "none",
                background: dynamicColor[props.userType].background,
                color: dynamicColor[props.userType].color,
                //outline: dynamicColor[props.userType].outline,
                "&:hover": {
                    textDecoration: "underline",
                    cursor: "pointer"
                },

            }}
            {...props}
        />
    )
}

export const LinkTypography = styled(Link)(({ theme }) => ({
    color: "rgb(59, 59, 59)"
}))

export const MenuIconButtonStyled = styled(Button)(({ theme }) => ({
    color: "black",
    "&:hover": {
        background: "rgba(0,0,0,0.2)"
    }
}))


export const SmallMenuBarUserName = styled(Typography)(({ theme }) => ({
    background: "#f0f0f0",
    textAlign: "center"
}))

export const DrawerStyled = styled(Drawer)(({ theme }) => ({
    [theme.breakpoints.up("lg")]: {
        display: "none"
    },
    // Move the mobile dropdown down
    // no other way to select it
    "& > .MuiPaper-root.MuiPaper-elevation.MuiPaper-elevation16.MuiDrawer-paper.MuiDrawer-paperAnchorTop.css-1nvnyqx-MuiPaper-root-MuiDrawer-paper": {
        [theme.breakpoints.down("lg")]: {
            top: "80px"
        },
        [theme.breakpoints.down("md")]: {
            top: "65px"
        }
    }
}))

export const ListStyled = styled(List)(({ theme }) => ({
    padding: "0",
}))

const dynamicColor = {
    "Student": {
        "background": "rgb(0, 163, 224)",
        "color": "white",
        "outline": "none",
    },
    "Independent": {
        "background": "rgb(255, 200, 0)",
        "color": "black",
        "outline": "none",
    },
    "Teacher": {
        "background": "rgb(224, 0, 77)",
        "color": "white",
        "outline": "none",
    },
    "None": {
        "background": "white",
        "color": "black",
        "outline": "2px solid rgb(255, 200, 0)"
    }
}

export const ListItemStyled: React.FC<User> = (props) => (

    <ListItem
        sx={{
            display: "flex",
            alignItems: "start",
            background: dynamicColor[props.userType].background,
            color: dynamicColor[props.userType].color,
            outline: dynamicColor[props.userType].outline,
            "&:hover": {
                cursor: "pointer",
            },
        }}
        // Make the component wrapping
        {...props}
    />
)

export const SubMenuStyled: React.FC<User> = props => (
    <ListItem
        sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "start",
            background: dynamicColor[props.userType].background,
            color: dynamicColor[props.userType].color,
            outline: dynamicColor[props.userType].outline,
            "&:hover": {
                cursor: "pointer",
            },
        }}
        // Make the component wrapping
        {...props}
    />
)


export const ListSingleItem = styled(ListItem)(({ theme }) => ({
    display: "flex",
    "&:hover": {
        cursor: "pointer",
        textDecoration: "underline",
    },
}))

export const ListItemIconStyled: React.FC<User> = props => (
    <ListItemIcon
        sx={{
            color: dynamicColor[props.userType].color,
            marginTop: "0.1rem"
        }}
        {...props}
    />
)


export const DropDownStyled = (props: any) => {

    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);

    const handleClose = () => {
        setAnchorEl(null);
    };
    (

        <Menu
            open={open}
            onClose={handleClose}
            sx={{
                "& > div > ul": {
                    paddingTop: "0",
                    paddingBottom: "0",
                    zIndex: "1500"
                }

            }}
            {...props}
        />
    )
}

export const SmallNavbarRegisterButton = styled("div")(({ theme }) => ({
    background: "rgb(255, 200, 0)"
}))

export const TypographyHover = styled(Typography)(({ theme }) => ({
    "&:hover": {
        textDecoration: "underlined"
    }
}))

export default AppBarStyled