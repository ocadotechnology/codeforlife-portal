import RegisterButtonStyled from './RegisterButtonStyled';
import React from 'react';

const RegisterButton: React.FC = () => {
    return (
        <RegisterButtonStyled
            variant="contained"
            color="secondary"

        >
            Register</RegisterButtonStyled>
    )
};

export default RegisterButton;
