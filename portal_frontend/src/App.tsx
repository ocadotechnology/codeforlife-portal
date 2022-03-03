/*

Libraries that seem to be breaking the app without notice

@material-ui/core
@mui/lab


*/
import Footer from "./Components/Footer/Footer";
import React from "react";
import theme from "./Theme";
import { ThemeProvider } from "@mui/material/styles";
import Navbar from "./Components/Navbar/Navbar";
import Welcome from "./Components/Banner/Welcome";
import RapidRouterScores from "./Components/RapidRouterScores/RapidRouterScores";
import KuronoWidget from "./Components/KuronoWidget/KuronoWidget";
import MeetTheCharacters from "./Components/MeetTheCharacters/MeetTheCharacters";

export type UserType = "student" | "independent" | "teacher" | "none";
export interface User {
  userType: UserType;
  name: string;
  children?: React.ReactNode;
}

let name: string = "Kamil Sosinski";
let userType: UserType = "independent";

const App = () => {
  return (
    <div>
      <ThemeProvider theme={theme}>
        <Navbar userType={userType} name={name} />
        <Welcome name={name} userType={userType} />
        <RapidRouterScores />
        <KuronoWidget />
        <MeetTheCharacters />
        <Footer />
      </ThemeProvider>
    </div>
  );
};

export default App;
