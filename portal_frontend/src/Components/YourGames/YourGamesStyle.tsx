import { styled } from "@mui/material/styles";
import { Card, Box, Button } from "@mui/material";

export const BoxStyled = styled(Box)(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  "& > h4": {
    textAlign: "center",
  },
}));

export const CardStyled = styled(Card)(({ theme }) => ({
  [theme.breakpoints.up("lg")]: {
    width: "min-content",
  },
  "& > h5": {
    padding: "1rem 0 1rem 1rem",
  },
  "& > p": {
    padding: "0 1rem 1rem 1rem",
  },
}));

export const ButtonStyled = styled(Button)(({ theme }) => ({
  margin: "1rem 1rem 1rem 1rem",
  width: "45%",
}));
