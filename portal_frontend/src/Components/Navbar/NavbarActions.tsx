import LogInButton from "./LogInButton";
import React from "react";
import RegisterButton from "./RegisterButton";
import { User } from "./Navbar";
import {
    ActionsStyled,
    ActionsTypographyStyled,
    NavbarMenuStyled,
} from "./NavbarStyle";

import { Button, Link, Typography } from "@mui/material";
import NavBarDropDown from "./NavBarDropDown";
import { LinkStyled } from "./NavbarStyle";

export const navbarActions = {
    Student: {
        navField: {
            text: ["Dashboard", "Games", "Scoreboard"],
            link: ["", "", ""],
        },
        games: {
            text: ["Rapid Router", "Kurono"],
            link: ["", ""],
        },
        resources: {
            text: [""],
            link: [""],
        },
    },
    Independent: {
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
    Teacher: {
        navField: {
            text: ["Dashboard", "Games", "Teaching Resources"],
            link: ["", "", ""],
        },
        games: {
            text: ["Rapid Router", "Kurono"],
            link: [""],
        },
        resources: {
            text: ["Rapid Router", "Kurono"],
            link: [""],
        },
    },
    None: {
        navField: {
            text: ["Teachers", "Students"],
            links: [
                "https://www.codeforlife.education/teach/",
                "https://www.codeforlife.education/play/",
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

interface StringBoolHash {
    [key: string]: boolean;
}

const NotDropDown: StringBoolHash = {
    Dashboard: true,
    Scoreboard: true,
};

const isGame = (text: string) => {
    return text === "Games" ? "games" : "resources";
};

const NavbarActions = ({ userType, userName }: User) => {
    return (
        <ActionsStyled>
            <ActionsTypographyStyled variant="h4">
                {userType !== "None" ? userType : null}
            </ActionsTypographyStyled>
            {userType === "None" ? (
                navbarActions[userType].navField.text.map(
                    (element: string, i: number) => {
                        return (
                            <LinkStyled
                                userType={userType}
                            // href={navbarActions[userType].navField.links[i]}
                            //    variant="h4"
                            >
                                {element}
                            </LinkStyled>
                        );
                    }
                )
            ) : (
                <>
                    {navbarActions[userType].navField.text.map(
                        (element: string, index: number) => {
                            return NotDropDown[element] ? (
                                <LinkStyled>{element}</LinkStyled>
                            ) : (
                                <NavBarDropDown
                                    title={element}
                                    subTitles={navbarActions[userType][isGame(element)].text}
                                />
                            );
                        }
                    )}
                </>
            )}
        </ActionsStyled>
    );
};

export default NavbarActions;
