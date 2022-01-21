import { styled } from "@mui/material/styles";
import { Box, Card } from "@mui/material";

export const BoxStyled = styled(Box)(({ theme }) => ({
	display: "flex",
	flexDirection: "column",
	justifyContent: "center",
	alignItems: "center",
	background: "rgb(240 240 240)",
	padding: "1rem 1rem 3rem 1rem",
}));

export const CardsStyled = styled(Card)(({ theme }) => ({
	display: "flex",
	flexDirection: "row",
}));

export const CardStyled = styled(Card)(({ theme }) => ({
	[theme.breakpoints.up("lg")]: {
		width: "300px",
		height: "625px",
	},
	alignItems: "center",
	padding: "1rem 1rem 1rem 1rem",
	display: "flex",
	flexDirection: "column",
}));
