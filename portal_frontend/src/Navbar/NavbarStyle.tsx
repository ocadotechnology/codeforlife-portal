import { MenuItem, Menu } from '@mui/material';
import { Button } from '@mui/material';
import React from 'react';
import { AppBar, Toolbar, IconButton, Typography } from '@mui/material';
import { styled } from "@mui/material/styles"

export const AppBarStyled = styled(AppBar)(({ theme }) => ({
    background: "white",
    color: "black",
    padding: "0px 0.5rem 0px 1rem"
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
        marginLeft: "5%"
    }
}))

export const IconButtonStyled = styled(IconButton)(({ theme }) => ({
    [theme.breakpoints.up("lg")]: {
        display: "none",
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
    fontWeight: "500"
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

export default AppBarStyled