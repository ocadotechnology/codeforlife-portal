import { styled } from "@mui/material/styles"
import { Button, Menu } from "@mui/material"

export const UserNameButtonStyled = styled(Button)(({ theme }) => ({
    color: "black",
    height: "45px",
    width: "17vw",
    display: "flex",
    justifyContent: "space-between",
    marginLeft: "auto",
    marginRight: "0",
    textTransform: "none",
    border: "2px solid rgb(255, 200, 0)",
    transition: "250ms",
    "&:hover": {
        textDecoration: "underline",
        background: "none",
    },
    [theme.breakpoints.down("lg")]: {
        display: "none"
    },
    "& > div > ul": {
        paddingTop: "0",
        paddingBottom: "0",
    }
}))

export const UserMenuStyled = styled(Menu)(({ theme }) => ({
    backgorund: "black",
    "& > div > ul": {
        paddingTop: "0",
        paddingBottom: "0",
    }
}))