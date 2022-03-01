import { User } from "../../App";
import {
    ActionsStyled,
    ActionsTypographyStyled,
} from "./NavbarStyle";

import NavBarDropDown from "./NavBarDropDown";
import { LinkStyled } from "./NavbarStyle";

export const navbarActions = {
    student: {
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
            text: ["Rapid Router", "Kurono"],
            link: [""],
        },
        resources: {
            text: ["Rapid Router", "Kurono"],
            link: [""],
        },
    },
    none: {
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

// Dashboard and Scoreboard buttons will
// not show as dropdowns on the navbar
const NotDropDown: StringBoolHash = {
    Dashboard: true,
    Scoreboard: true,
};

const isGame = (text: string) => {
    return text === "Games" ? "games" : "resources";
};

// Responsible for all the actions on the left side of
// the navbar after the ocado logo.
const NavbarActions = ({ userType, userName }: User) => {
    return (
        <ActionsStyled>
            <ActionsTypographyStyled variant="h4">
                { // This is the title of what user type is
                    // logged in i.e Student, Teacher, Independent or not logged
                    userType !== "none" ? userType.charAt(0).toUpperCase() + userType.slice(1) : null
                }
            </ActionsTypographyStyled>
            { // If not logged in, Teacher
                // and Student links returned
                userType === "none" ? (
                    navbarActions[userType].navField.text.map(
                        (element: string, i: number) => {
                            return (
                                <LinkStyled
                                    userType={userType}
                                    href={navbarActions[userType].navField.links[i]}
                                    variant="h4"
                                >
                                    {element}
                                </LinkStyled>
                            );
                        }
                    )
                ) : (
                    <>
                        { // else return the user actions with
                            // their dropdown buttons if they're needed
                            navbarActions[userType].navField.text.map(
                                (element: string, index: number) => {
                                    return NotDropDown[element] ? (
                                        <LinkStyled variant="body1">{element}</LinkStyled>
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
