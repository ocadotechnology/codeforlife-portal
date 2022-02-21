import { styled } from "@mui/material/styles";
import { Box, Paper } from "@mui/material";

export const StyledBox = styled(Box)(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  "& > img": {
    width: "20%",
  },
  "& > h4": {
    width: "60%",
    textAlign: "center",
  },
}));

export const PaperStyled = styled(Paper)(({ theme }) => ({
  margin: "2rem 0 2rem 0",
}));
