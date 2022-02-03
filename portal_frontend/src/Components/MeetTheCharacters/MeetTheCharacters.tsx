import React from "react";
import { BoxStyled } from "./MeetTheCharactersStyle";
import Cards from "./Cards";
import { Typography } from "@mui/material";

const MeetTheCharacters = () => {
  return (
    <BoxStyled>
      <Typography variant="h4">Meet the characters</Typography>
      <Cards />
    </BoxStyled>
  );
};

export default MeetTheCharacters;
