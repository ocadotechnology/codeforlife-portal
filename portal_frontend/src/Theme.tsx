import { createTheme } from "@mui/material/styles";

const FONT_FAMILY = '"Space Grotesk", sans-serif';

export const theme = createTheme({
  // Paste the code below this line
  // from https://bareynol.github.io/mui-theme-creator/?firstName=&lastName=&email=&password=
  palette: {
    primary: {
      main: "rgb(244, 0, 77)",
    },
    secondary: {
      main: "rgb(255, 200, 0)",
    },
  },
  typography: {
    h1: {
      fontFamily: FONT_FAMILY,
    },
    h2: {
      fontFamily: FONT_FAMILY,
    },
    h3: {
      fontFamily: FONT_FAMILY,
    },
    h4: {
      fontFamily: FONT_FAMILY,
    },
    h5: {
      fontFamily: FONT_FAMILY,
    },
    h6: {
      fontFamily: FONT_FAMILY,
    },
    subtitle1: {
      fontFamily: FONT_FAMILY,
    },
    subtitle2: {
      fontFamily: FONT_FAMILY,
    },
    body1: {
      fontFamily: FONT_FAMILY,
    },
    body2: {
      fontFamily: FONT_FAMILY,
    },
    button: {
      fontFamily: FONT_FAMILY,
    },
    caption: {
      fontFamily: FONT_FAMILY,
    },
    overline: {
      fontFamily: FONT_FAMILY,
    },
  },
});

export default theme;
