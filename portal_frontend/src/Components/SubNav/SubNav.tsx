import { styled, ToggleButton, ToggleButtonGroup } from "@mui/material";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import React from "react";
import secondaryColour from "../../colours/secondary";
import SubNavItem from "./SubNavItem";

const StyledToggleButtonGroup = styled(ToggleButtonGroup)(({ theme }) => ({
  display: "flex",
  backgroundColor: secondaryColour[300], // TODO: user colour
  justifyContent: "center",
  alignItems: "center",
  height: 60,
  "& .MuiToggleButtonGroup-grouped": {
    textTransform: "none",
    margin: theme.spacing(2),
    height: 42,
    minWidth: 150,
    color: theme.palette.secondary.contrastText,
    borderRadius: 0,
    "&:first-of-type, &:not(:first-of-type)": {
      borderWidth: 1,
      borderColor: theme.palette.secondary.contrastText,
    },
    "&.Mui-selected": {
      color: secondaryColour[300],
      backgroundColor: theme.palette.secondary.contrastText,
    },
  },
}));

const SubNav = () => {
  const [subNavItem, setSubNavItem] = React.useState("levels");

  const handleSubNavItem = (
    event: React.MouseEvent<HTMLElement, MouseEvent>,
    newSubNavItem: string
  ) => {
    if (newSubNavItem !== null) {
      setSubNavItem(newSubNavItem);
    }
  };

  return (
    <StyledToggleButtonGroup
      value={subNavItem}
      exclusive
      onChange={handleSubNavItem}
      aria-label="subnav"
    >
      {/* <Stack
        direction="row"
        spacing={2}
        sx={{
          bgcolor: secondaryColour[300], // TODO: user colour
          justifyContent: "center",
          alignItems: "center",
          height: 60,
        }}
        // color="secondary"
      > */}
      {/* <SubNavItem>Levels</SubNavItem>
        <SubNavItem>Create</SubNavItem> */}
      <ToggleButton value="levels" aria-label="levels">
        Levels
      </ToggleButton>
      <ToggleButton value="create" aria-label="create">
        Create
      </ToggleButton>
      {/* </Stack> */}
    </StyledToggleButtonGroup>
  );
};

export default SubNav;
