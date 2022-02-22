import { createTheme } from "@mui/material/styles";


const FONT_PRIMARY: string = '"Space Grotesk", sans-serif';
const FONT_SECONDARY: string = '"Inter", sans-serif';

const MEDIUM: number = 500
const SEMI_BOLD: number = 600
const BOLD: number = 700

const FONT_COLOR: string = "rgb(56, 59, 59)"


export const theme = createTheme({
  // Paste the code below this line
  // from https://bareynol.github.io/mui-theme-creator/
  palette: {
    primary: {
      main: "rgb(244, 0, 77)",
    },
    secondary: {
      main: "rgb(255, 200, 0)",
    },
    neutral: {
      main: "rgb(59, 59, 59)",
    }
  },
  typography: {
    h1: {
      fontFamily: FONT_PRIMARY,
      fontSize: "65px",
      fontWeight: MEDIUM,
    },
    h2: {
      fontFamily: FONT_PRIMARY,
      fontSize: "55px",
      fontWeight: MEDIUM,
    },
    h3: {
      fontFamily: FONT_PRIMARY,
      fontSize: "45px",
      fontWeight: MEDIUM,
    },
    h4: {
      fontFamily: FONT_PRIMARY,
      fontSize: "30px",
      fontWeight: MEDIUM,
    },
    h5: {
      fontFamily: FONT_PRIMARY,
      fontSize: "24px",
      fontWeight: MEDIUM,
    },
    h6: {
      fontFamily: FONT_PRIMARY,
      fontSize: "20px",
      fontWeight: MEDIUM,
    },
    subtitle1: {
      fontFamily: FONT_SECONDARY,
      fontSize: "22px",
    },
    subtitle2: {
      fontFamily: FONT_SECONDARY,
      fontSize: "20px",
      fontWeight: MEDIUM,
    },
    bodyText1: {
      fontFamily: FONT_SECONDARY,
      fontSize: "18px"
    },
    bodyText2: {
      fontFamily: FONT_SECONDARY,
      fontSize: "16px",
    },
    // This has to be button as otherwise
    // the buttons will not get styled at all
    button: {
      fontFamily: FONT_SECONDARY,
      fontSize: "16px",
      fontWeight: SEMI_BOLD,
    },
    caption: {
      fontFamily: FONT_SECONDARY,
      fontSize: "13px"
    },
    overline: {
      fontFamily: FONT_SECONDARY,
      fontSize: "10px",
      fontWeight: MEDIUM,
    },
    quote: {
      fontSize: "20px"
    }
  },
});

export default theme;
