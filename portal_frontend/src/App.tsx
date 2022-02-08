/*

Libraries that seem to be breaking the app without notice

@material-ui/core
@mui/lab


*/

import { Container } from "@mui/material";
import React from "react";
import Footer from "./Components/Footer/Footer";
import Navbar from "./Components/Navbar/Navbar";
import theme from "./Theme";
import { ThemeProvider } from "@mui/material/styles";
import Welcome from "./Components/Welcome/Welcome";
import YourGames from "./Components/YourGames/YourGames";
import RapidRouterScores from "./Components/RapidRouterScores/RapidRouterScores";
import KuronoWidget from "./Components/KuronoWidget/KuronoWidget";
import MeetTheCharacters from "./Components/MeetTheCharacters/MeetTheCharacters";

type UserType = "student" | "independent" | "teacher";

let name: string = "First Name";
let userType: UserType = "independent";

const App: React.FC = () => {
  return (
    <div>
      <ThemeProvider theme={theme}>
        <Navbar name={name} userType={userType} />
        <Welcome name={name} />
        <Container
          sx={{
            display: "flex",
            flexDirection: "column",
            padding: "5% 0 5% 0",
            width: "70%",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <YourGames />
        </Container>
        <RapidRouterScores />
        <KuronoWidget />
        <MeetTheCharacters />
        <Footer />
      </ThemeProvider>
    </div>
  );
};

export default App;
