import { createTheme } from "@mui/material/styles";

const SPACE_GROTESK: string = '"Space Grotesk", sans-serif';
const INTER: string = '"Inter", sans-serif';

const MEDIUM: number = 500
const SEMI_BOLD: number = 600
const BOLD: number = 700


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
  },
  typography: {
    h1: {
      fontFamily: SPACE_GROTESK,
      fontSize: "65px",
      fontWeight: MEDIUM,
    },
    h2: {
      fontFamily: SPACE_GROTESK,
      fontSize: "55px",
      fontWeight: MEDIUM,
    },
    h3: {
      fontFamily: SPACE_GROTESK,
      fontSize: "45px",
      fontWeight: MEDIUM,
    },
    h4: {
      fontFamily: SPACE_GROTESK,
      fontSize: "30px",
      fontWeight: MEDIUM,
    },
    h5: {
      fontFamily: SPACE_GROTESK,
      fontSize: "24px",
      fontWeight: MEDIUM,
    },
    h6: {
      fontFamily: SPACE_GROTESK,
      fontSize: "20px",
      fontWeight: MEDIUM,
    },
    subtitle1: {
      fontFamily: INTER,
      fontSize: "22px",
    },
    subtitle2: {
      fontFamily: INTER,
      fontSize: "20px",
      fontWeight: MEDIUM,
    },
    bodyText1: {
      fontFamily: INTER,
      fontSize: "18px"
    },
    bodyText2: {
      fontFamily: INTER,
      fontSize: "16px",
    },
    quote: {
      fontFamily: SPACE_GROTESK,
      fontSize: "24px",
      fontWeight: MEDIUM
    },
    buttonText: {
      fontFamily: INTER,
      fontSize: "16px",
      fontWeight: SEMI_BOLD,
    },
    caption: {
      fontFamily: INTER,
      fontSize: "13px"
    },
    overline: {
      fontFamily: INTER,
      fontSize: "10px",
      fontWeight: MEDIUM,
    },
  },
});

export default theme;
