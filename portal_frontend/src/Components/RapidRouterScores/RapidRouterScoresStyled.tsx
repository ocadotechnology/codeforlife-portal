import { styled } from "@mui/material/styles";
import { Box } from "@mui/material";

export const StyledBox = styled(Box)(({ theme }) => ({
	margin: "1rem 1rem 1rem 1rem",
	background: "#f1ecec",
	display: "flex",
	flexDirection: "column",
	justifyContent: "center",
	alignItems: "center",
	"& > h4": {
		margin: "1rem 0 1rem 0",
	},
}));
