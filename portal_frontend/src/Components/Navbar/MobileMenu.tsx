import React, { useState } from "react";
import {
  LinkStyled,
  ListSingleItem,
  ListStyled,
  SubMenuStyled,
} from "./NavbarStyle";
import { ListItemIcon } from "@mui/material";
import { User } from "../../App";
import RegisterButton from "./RegisterButton";
import LogInButton from "./LogInButton";
import { Collapse } from "@mui/material";
import { ListItemStyled, ListItemIconStyled } from "./NavbarStyle";
import { Typography, Box } from "@mui/material";

import SchoolOutlinedIcon from "@mui/icons-material/SchoolOutlined";
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
import GridViewOutlinedIcon from "@mui/icons-material/GridViewOutlined";
import SportsEsportsOutlinedIcon from "@mui/icons-material/SportsEsportsOutlined";
import ArticleNavbarActionsOutlinedIcon from "@mui/icons-material/ArticleOutlined";

interface StringBoolHash {
  [key: string]: boolean;
}
const IsDropDown: StringBoolHash = {
  Games: true,
  "Teaching Resources": true,
  "Learning Resources": true,
};
const MobileMenu = ({ userType, name }: User) => {
  const isGame = (text: string) => {
    return text === "Games" ? "games" : "resources";
  };

  const dynamicContentIcons = [
    <GridViewOutlinedIcon />,
    <SportsEsportsOutlinedIcon />,
    <ArticleNavbarActionsOutlinedIcon />,
  ];
  // TODO - All the links need to eventually be relative path, as we need them to work locally and on staging as well.
  const dynamicContent = {
    student: {
      navField: {
        text: ["Dashboard", "Games", "Scoreboard"],
        link: [
          "https://www.codeforlife.education/teach/dashboard/#school",
          "",
          "",
        ],
      },
      games: {
        text: ["Rapid Router"],
        link: ["https://www.codeforlife.education/rapidrouter/"],
      },
      resources: {
        text: ["Rapid Router"],
        link: [""],
      },
    },
    independent: {
      navField: {
        text: ["Dashboard", "Games", "Learning Resources"],
        link: ["", "", ""],
      },
      games: {
        text: ["Rapid Router"],
        link: [""],
      },
      resources: {
        text: ["Rapid Router"],
        link: [""],
      },
    },
    teacher: {
      navField: {
        text: ["Dashboard", "Games", "Teaching Resources"],
        link: ["", "", ""],
      },
      games: {
        text: ["Rapid Router"],
        link: ["https://www.codeforlife.education/rapidrouter/"],
      },
      resources: {
        text: ["Rapid Router", "Kurono"],
        link: ["", ""],
      },
    },
    none: {
      navField: {
        text: ["Teacher", "Student", "Independent"],
        link: [
          "https://www.codeforlife.education/login/teacher/",
          "https://www.codeforlife.education/login/student/",
          "https://www.codeforlife.education/login/independent/",
        ],
      },
      games: {
        text: [""],
        link: [""],
      },
      resources: {
        text: [""],
        link: [""],
      },
    },
  };

  const [menu, setMenu] = useState(false);
  const [games, setGames] = useState(false);
  const [resources, setResources] = useState(false);

  return (
    <ListStyled>
      {userType !== "none" ? (
        <ListSingleItem onClick={() => setMenu(!menu)}>
          <ListItemIcon>
            {userType === "teacher" ? (
              <PersonOutlinedIcon />
            ) : (
              <SchoolOutlinedIcon />
            )}
          </ListItemIcon>
          <Typography variant="subtitle2">
            {userType.charAt(0).toUpperCase() + userType.slice(1)}
          </Typography>
        </ListSingleItem>
      ) : (
        <div>
          <RegisterButton />
          <div onClick={() => setMenu(!menu)}>
            <LogInButton smallScreen={true} />
          </div>
        </div>
      )}
      <Collapse in={menu}>
        <Box>
          {dynamicContent[userType].navField.text.map((text, index) => (
            <ListItemStyled name={name} userType={userType} key={text}>
              <ListItemIconStyled name={name} userType={userType}>
                {dynamicContentIcons[index]}
              </ListItemIconStyled>
              {
                // Dashboard and Scoreboard never have dropdown buttons
                IsDropDown[text] ? (
                  // Alter between games and resources
                  <div
                    onClick={() =>
                      text === "Games"
                        ? setGames(!games)
                        : setResources(!resources)
                    }
                  >
                    <LinkStyled userType={userType} variant="subtitle2">
                      {text}
                    </LinkStyled>
                    <Collapse
                      orientation="vertical"
                      in={text === "Games" ? games : resources}
                    >
                      <SubMenuStyled name={name} userType={userType}>
                        {dynamicContent[userType][isGame(text)].text.map(
                          (element: string, index: number) => {
                            return (
                              <LinkStyled
                                href={
                                  dynamicContent[userType][isGame(text)].link[
                                  index
                                  ]
                                }
                                userType={userType}
                                variant="subtitle2"
                              >
                                {element}
                              </LinkStyled>
                            );
                          }
                        )}
                      </SubMenuStyled>
                    </Collapse>
                  </div>
                ) : (
                  <LinkStyled
                    href={
                      userType === "none"
                        ? dynamicContent[userType].navField.text[index]
                        : ""
                    }
                    userType={userType}
                    variant="subtitle2"
                  >
                    {text}
                  </LinkStyled>
                )
              }
            </ListItemStyled>
          ))}
        </Box>
      </Collapse>
    </ListStyled>
  );
};

export default MobileMenu;
