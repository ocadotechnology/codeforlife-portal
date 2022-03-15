import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import secondaryColour from "../../colours/secondary";

const SubNav = () => {
  return (
    <Stack
      direction="row"
      spacing={2}
      sx={{
        bgcolor: secondaryColour[300], // TODO: user colour
        justifyContent: "center",
        alignItems: "center",
        height: 60,
      }}
      // color="secondary"
    >
      <Button variant="outlined" color="inherit">
        Levels
      </Button>
      <Button variant="outlined" color="secondary">
        Create
      </Button>
    </Stack>
  );
};

export default SubNav;
