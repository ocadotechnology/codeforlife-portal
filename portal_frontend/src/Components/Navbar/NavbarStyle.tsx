import {
    MenuItem,
    Menu,
    Button,
    AppBar,
    Toolbar,
    IconButton,
    Typography,
    Link,
    Drawer,
    List,
    ListItem,
    ListItemIcon,
} from "@mui/material";
import React from "react";
import { styled } from "@mui/material/styles";
import { UserType, User } from "../../App";
import { useState } from "react";
import { OverridableStringUnion } from "@mui/types/index";
import { TypographyPropsVariantOverrides } from "@mui/material/Typography";
import { Variant } from "@mui/material/styles/createTypography";

import theme from "../../Theme";

export const AppBarStyled = styled(AppBar)(({ theme }) => ({
    zIndex: "1201",
    background: "white",
    color: "black",
    padding: "0px 0px 0px 1rem",
}));

export const ToolbarStyled = styled(Toolbar)(({ theme }) => ({
    display: "flex",
    flexDirection: "row",
    [theme.breakpoints.up("lg")]: {
        height: "100px",
        justifyContent: "start",
    },
    [theme.breakpoints.down("lg")]: {
        height: "80px",
        justifyContent: "space-between",
    },
    [theme.breakpoints.down("md")]: {
        height: "65px",
        justifyContent: "space-between",
    },
    "& > button": {
        [theme.breakpoints.up("lg")]: {
            marginLeft: "auto",
        },
    },
}));

export const LogoCfl = styled("img")(({ theme }) => ({
    [theme.breakpoints.up("lg")]: {
        height: "70px",
    },
    [theme.breakpoints.only("md")]: {
        height: "70px",
    },
    [theme.breakpoints.down("md")]: {
        height: "50px",
    },
}));

export const LogoOcado = styled("img")(({ theme }) => ({
    [theme.breakpoints.up("lg")]: {
        height: "52px",
        marginLeft: "4rem",
    },
}));

export const IconButtonStyled = styled(IconButton)(({ theme }) => ({
    [theme.breakpoints.up("lg")]: {
        display: "none",
    },
    "&:hover": {
        background: "none",
    },
}));

export const ActionsStyled = styled("div")(({ theme }) => ({
    display: "flex",
    alignItems: "baseline",
    flexDirection: "row",
    [theme.breakpoints.down("lg")]: {
        display: "none",
    },
}));

export const ActionsTypographyStyled = styled(Typography)(({ theme }) => ({
    margin: "2rem",
}));

export const NavBarButtonStyled = styled(Button)(({ theme }) => ({
    color: "black",
    textTransform: "none",
    fontWeight: "500",
    "&:hover": {
        background: "none",
        textDecoration: "underline",
    },
}));

export const NavButtonItemStyled = styled(MenuItem)(({ theme }) => ({
    "&:hover": {
        background: "none",
        textDecoration: "underline",
    },
}));
export const NavbarMenuStyled = styled(Menu)(({ theme }) => ({
    "& > div > ul": {
        padding: "0, 3rem, 0, 1rem",
    },
}));

interface LinkAttr {
    variant?: OverridableStringUnion<
        Variant | "inherit",
        TypographyPropsVariantOverrides
    >;
    href?: string;
    userType?: UserType | undefined;
    children?: React.ReactNode
}

export const LinkStyled = (props: LinkAttr) => {
    return (
        <Link
            href={props.href}
            variant={props.variant}
            sx={{
                marginRight: "1rem",
                textDecoration: "none",
                background: props.userType === undefined ? "none" : dynamicColor[props.userType].background,
                color: props.userType === undefined ? "black" : dynamicColor[props.userType].color,
                outline: props.userType === undefined ? "none" : dynamicColor[props.userType].outline,
                "&:hover": {
                    textDecoration: "underline",
                    cursor: "pointer",
                },
            }}
            {...props}
        />
    );
};

export const LinkTypography = styled(Link)(({ theme }) => ({
    color: "grey",
}));

export const MenuIconButtonStyled = styled(Button)(({ theme }) => ({
    color: "black",
}));

export const SmallMenuBarUserName = styled(Typography)(({ theme }) => ({
    background: "#f0f0f0",
    textAlign: "center",
}));

export const DrawerStyled = styled(Drawer)(({ theme }) => ({
    [theme.breakpoints.up("lg")]: {
        display: "none",
    },
    // Move the mobile dropdown down
    // no other way to select it
    "& > .MuiPaper-root.MuiPaper-elevation.MuiPaper-elevation16.MuiDrawer-paper.MuiDrawer-paperAnchorTop.css-1nvnyqx-MuiPaper-root-MuiDrawer-paper":
    {
        [theme.breakpoints.down("lg")]: {
            top: "80px",
        },
        [theme.breakpoints.down("md")]: {
            top: "65px",
        },
    },
}));

export const ListStyled = styled(List)(({ theme }) => ({
    padding: "0",
}));

// TODO: make the colours work with
// the theme object from Theme.tsx
const dynamicColor = {
    student: {
        background: "#00a3e0",
        color: "white",
        outline: "none",
    },
    independent: {
        background: "rgb(255, 200, 0)",
        color: "black",
        outline: "none",
    },
    teacher: {
        background: "rgb(224, 0, 77)",
        color: "white",
        outline: "none",
    },
    none: {
        background: "white",
        color: "black",
        outline: `2px solid ${theme.palette.secondary.main}`,
    },
};

export const ListItemStyled = (props: User) => (
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
);

export const SubMenuStyled = (props: User) => (
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
);

export const ListSingleItem = styled(ListItem)(({ theme }) => ({
    display: "flex",
    "&:hover": {
        cursor: "pointer",
        textDecoration: "underline",
    },
}));

export const ListItemIconStyled: React.FC<User> = (props) => (
    <ListItemIcon
        sx={{
            color: dynamicColor[props.userType].color,
            marginTop: "0.1rem",
        }}
        {...props}
    />
);

export const DropDownStyled = (props: any) => {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);

    const handleClose = () => {
        setAnchorEl(null);
    };
    <Menu
        open={open}
        onClose={handleClose}
        sx={{
            "& > div > ul": {
                paddingTop: "0",
                paddingBottom: "0",
                zIndex: "1500",
            },
        }}
        {...props}
    />;
};

export const SmallNavbarRegisterButton = styled("div")(({ theme }) => ({
    background: theme.palette.primary.main,
}));

export const TypographyHover = styled(Typography)(({ theme }) => ({
    "&:hover": {
        textDecoration: "underlined",
    },
}));

export const SubButtonStyled = styled(MenuItem)(({ theme }) => ({
    borderRadius: "0",
    width: "155px",
    fontSize: "15px",
    border: theme.palette.primary.main,
    display: "flex",
    justifyContent: "space-between",
    "&:hover": {
        background: "white",
        textDecoration: "underline",
    },
}));

export const LogInButtonStyled = styled(Button)(({ theme }) => ({
    borderRight: "0",
    color: "black",
    borderRadius: "0",
    height: "45px",
    width: "155px",
    marginLeft: "10%",
    textTransform: "none",
    border: `2px solid ${theme.palette.secondary.main}`,
    transition: "250ms",
    "&:hover": {
        border: `2px solid ${theme.palette.secondary.main}`,
        textDecoration: "underline",
        background: "none",
    },
    [theme.breakpoints.down("lg")]: {
        width: "100%",
        marginLeft: "0",
        border: "none",
    },
}));

export const LogInMenuStyled = styled(Menu)(({ theme }) => ({
    "& > div > ul": {
        paddingTop: "0",
        paddingBottom: "0",
        zIndex: "1500",
    },
}));

export const MenuItemStyled = styled(MenuItem)(({ theme }) => ({
    width: "155px",
    border: `2px solid ${theme.palette.secondary.main}`,
}));

export const UserItemStyled = styled(Button)(({ theme }) => ({
    borderRadius: "0",
    textAlign: "left",
    display: "flex",
    border: `2px solid ${theme.palette.secondary.main}`,
    color: "black",
    textTransform: "none",
    justifyContent: "space-between",
    width: "17vw",
    fontWeight: "100",
    padding: "0.5rem 1rem 0.5rem 1rem",
    "&:hover": {
        background: "none",
    },
}));

export const UserButtonDivStyled = styled("div")(({ theme }) => ({
    display: "flex",
    marginRight: "2rem",
    flexDirection: "row",
    [theme.breakpoints.up("lg")]: {
        marginLeft: "auto",
    },
    [theme.breakpoints.down("lg")]: {
        display: "none",
    },
}));

export const NotLoggedInStyled = styled("div")(({ theme }) => ({
    display: "flex",
    marginRight: "2rem",
    flexDirection: "row",
    [theme.breakpoints.up("lg")]: {
        marginLeft: "auto",
    },
    [theme.breakpoints.down("lg")]: {
        display: "none",
    },
}));

export const RegisterButtonStyled = styled(Button)(({ theme }) => ({
    marginLeft: "auto",
    height: "45px",
    width: "155px",
    textTransform: "none",
    borderRadius: "0",
    [theme.breakpoints.up("lg")]: {
        marginLeft: "auto",
    },
    [theme.breakpoints.down("lg")]: {
        width: "100%",
        height: "60px",
    },
    "&:hover": {
        boxShadow:
            "0px 6px 10px 0px rgba(0,0,0,0.14),0px 1px 18px 0px rgba(0,0,0,0.12),0px 3px 5px 0px rgba(0,0,0,0.2)",
        background: `${theme.palette.secondary.main}`,
    },
}));

export const RegisterButtonSmallMenuStyled = styled(RegisterButtonStyled)(
    ({ theme }) => ({
        marginLeft: "0",
    })
);

export const UserNameButtonStyled = styled(Button)(({ theme }) => ({
    color: "black",
    padding: "0.5rem 1rem 0.5rem 1rem",
    borderRadius: "0",
    height: "45px",
    width: "17vw",
    display: "flex",
    justifyContent: "space-between",
    marginLeft: "auto",
    marginRight: "0",
    textTransform: "none",
    border: `2px solid ${theme.palette.secondary.main}`,
    transition: "250ms",
    "&:hover": {
        textDecoration: "underline",
        background: "none",
    },
    [theme.breakpoints.down("lg")]: {
        display: "none",
    },
    "& > div > ul": {
        paddingTop: "0",
        paddingBottom: "0",
    },
}));

export const UserMenuStyled = styled(Menu)(({ theme }) => ({
    backgorund: "black",
    "& > div > ul": {
        paddingTop: "0",
        paddingBottom: "0",
    },
}));

export default AppBarStyled;
