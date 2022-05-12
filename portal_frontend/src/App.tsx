/*

Libraries that seem to be breaking the app without notice

@material-ui/core
@mui/lab


*/
import { ThemeProvider } from "@mui/material/styles";
import RapidRouter from "Components/Banner/RapidRouter";
import React from "react";
import Footer from "./Components/Footer/Footer";
import KuronoWidget from "./Components/KuronoWidget/KuronoWidget";
import MeetTheCharacters from "./Components/MeetTheCharacters/MeetTheCharacters";
import Navbar from "./Components/Navbar/Navbar";
import RapidRouterScores from "./Components/RapidRouterScores/RapidRouterScores";
import SubNav from "./Components/SubNav/SubNav";
import SubNavItem from "./Components/SubNav/SubNavItem";
import theme from "./Theme";
import "./portal.css";
import Welcome from "Components/Banner/Welcome";

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
        <SubNav userType={userType} initialValue="levels">
          <SubNavItem value="levels" aria-label="levels">
            Levels
          </SubNavItem>
          <SubNavItem value="create" aria-label="create">
            Create
          </SubNavItem>
          <SubNavItem value="scoreboard" aria-label="scoreboard">
            Scoreboard
          </SubNavItem>
        </SubNav>
        <RapidRouterScores />
        <KuronoWidget />
        <MeetTheCharacters />
        <Footer />
      </ThemeProvider>
    </div>
  );
};

export default App;
