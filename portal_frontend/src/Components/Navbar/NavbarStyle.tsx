import { styled } from "@mui/material/styles";
import { Button, Paper } from "@mui/material";
import { Menu } from "@mui/material";

import MenuIcon from "@mui/icons-material/Menu";

export const NavBarStyled = styled(Paper)(({ theme }) => ({
	display: "flex",
	flexDirection: "row",
	[theme.breakpoints.down("md")]: {
		justifyContent: "space-between",
	},
	"& > img": {
		padding: "0 1rem 0 1rem",
	},
	alignItems: "center",
	width: "100%",
}));

export const MenuIconStyled = styled(MenuIcon)(({ theme }) => ({
	[theme.breakpoints.up("md")]: {
		display: "none",
	},
}));

export const MenuWrap = styled("div")(({ theme }) => ({
	display: "flex",
	flexDirection: "row",
	"& > button": {
		padding: "1rem 3rem 1rem 3rem",
		fontSize: "20px",
	},
	[theme.breakpoints.down("md")]: {
		display: "none",
	},
}));

export const UserButtonStyled = styled(Button)(({ theme }) => ({
	color: "black",
	display: "flex",
	flexDirection: "row",
	justifyContent: "space-between",
	width: "18%",
	margin: "1rem 1rem 1rem 1rem",
	padding: "1rem 1rem 1rem 1rem",
}));

export const MenuStyled = styled(Menu)(({ theme }) => ({
	display: "flex",
	"& > button": {
		background: "green",
	},
}));
