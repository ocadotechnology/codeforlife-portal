import { createTheme, responsiveFontSizes } from "@mui/material/styles";

const FONT_PRIMARY: string = '"Space Grotesk", sans-serif';
const FONT_SECONDARY: string = '"Inter", sans-serif';

const MEDIUM: number = 500;
const SEMI_BOLD: number = 600;

let theme = createTheme({
  // Paste the code below this line
  // from https://bareynol.github.io/mui-theme-creator/
  palette: {
    primary: {
      main: "#e0004d",
      contrastText: "#fff",
    },
    secondary: {
      main: "#f6be00",
      contrastText: "#000",
    },
    tertiary: {
      main: "#00a3e0",
      contrastText: "#fff",
    },
    text: {
      primary: "#383b3b"
    }
  },
  typography: {
    h1: {
      fontFamily: FONT_PRIMARY,
      fontSize: "60px",
      fontWeight: MEDIUM,
      margin: "1rem 0 1rem 0"
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
    body1: {
      fontFamily: FONT_SECONDARY,
      fontSize: "18px",
    },
    body2: {
      fontFamily: FONT_SECONDARY,
      fontSize: "16px",
    },
    quote: {
      fontFamily: FONT_PRIMARY,
      fontSize: "24px",
      fontWeight: MEDIUM,
    },
    button: {
      fontFamily: FONT_SECONDARY,
      fontSize: "16px",
      fontWeight: SEMI_BOLD,
    },
    caption: {
      fontFamily: FONT_SECONDARY,
      fontSize: "13px",
    },
    overline: {
      fontFamily: FONT_SECONDARY,
      fontSize: "10px",
      fontWeight: MEDIUM,
    },
  },
});

theme = responsiveFontSizes(theme);

export default theme;
