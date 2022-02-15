/*

Libraries that seem to be breaking the app without notice

@material-ui/core
@mui/lab


*/

import React from "react";
import theme from "./Theme";
import { ThemeProvider } from "@mui/material/styles";
import Navbar from "./Navbar/Navbar"

const App: React.FC = () => {
  return (
    <div>
      <ThemeProvider theme={theme}>
        <Navbar userType="Teacher" userName="Put your name here :)" />
      </ThemeProvider>
    </div>
  );
};

export default App;
