import { styled } from "@mui/material/styles"
import { Button } from "@mui/material"
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';


export const SubButtonStyled = styled(MenuItem)(({ theme }) => ({
    width: "155px",
    fontSize: "15px",
    border: "2px solid rgb(255, 200, 0)",
    display: "flex",
    justifyContent: "space-between",
    "&:hover": {
        background: "white",
        textDecoration: "underline"
    }
}))

export const LogInButtonStyled = styled(Button)(({ theme }) => ({

    color: "black",
    height: "45px",
    width: "155px",
    marginLeft: "10%",
    textTransform: "none",
    border: "2px solid rgb(255, 200, 0)",
    transition: "250ms",
    "&:hover": {
        border: "2px solid rgb(255, 200, 0)",
        textDecoration: "underline",
        background: "none"
    },
    [theme.breakpoints.down("lg")]: {
        display: "none"
    }
}))

export const LogInMenuStyled = styled(Menu)(({ theme }) => ({
    "& > div > ul": {
        paddingTop: "0",
        paddingBottom: "0",
    }
}))

export const MenuItemStyled = styled(MenuItem)(({ theme }) => ({
    width: "155px",
    border: "2px solid rgb(255, 200, 0)"
}))

export const UserItemStyled = styled(Button)(({ theme }) => ({
    display: "flex",
    width: "310px",
    border: "2px solid rgb(255, 200, 0)",
    color: "black",
    textTransform: "none",
    justifyContent: "space-between"
}))

export const UserButtonDivStyled = styled("div")(({ theme }) => ({
    display: "flex",
    marginRight: "2rem",
    flexDirection: "row",
    [theme.breakpoints.up("lg")]: {
        marginLeft: "auto",
    },
    [theme.breakpoints.down("lg")]: {
        display: "none"
    }
}))

export const NotLoggedInStyled = styled("div")(({ theme }) => ({
    display: "flex",
    marginRight: "2rem",
    flexDirection: "row",
    [theme.breakpoints.up("lg")]: {
        marginLeft: "auto",
    },
    [theme.breakpoints.down("lg")]: {
        display: "none"
    }
}))