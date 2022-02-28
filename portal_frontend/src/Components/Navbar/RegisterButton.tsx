import { RegisterButtonStyled } from "./NavbarStyle";
import React from "react";

interface OnClick {
    onClick?: (anchor: string, on: boolean) => void;
    anchor?: string;
    on?: boolean;
}

const RegisterButton = () => {
    return (
        <RegisterButtonStyled variant="contained" color="secondary">
            Register
        </RegisterButtonStyled>
    );
};

export default RegisterButton;
