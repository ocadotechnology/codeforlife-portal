import { styled } from "@mui/material/styles"
import { Button } from "@mui/material"


export const RegisterButtonStyled = styled(Button)(({ theme }) => ({
    marginLeft: "auto",
    height: "45px",
    width: "155px",
    textTransform: "none",
    [theme.breakpoints.up("lg")]: {
        marginLeft: "auto"
    },
    [theme.breakpoints.down("lg")]: {
        display: "none"
    }
}))

export default RegisterButtonStyled