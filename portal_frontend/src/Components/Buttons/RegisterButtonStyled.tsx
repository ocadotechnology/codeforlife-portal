import { styled } from "@mui/material/styles"
import { Button } from "@mui/material"


export const RegisterButtonStyled = styled(Button)(({ theme }) => ({
    marginLeft: "auto",
    height: "45px",
    width: "155px",
    textTransform: "none",
    borderRadius: "0",
    [theme.breakpoints.up("lg")]: {
        marginLeft: "auto"
    },
    [theme.breakpoints.down("lg")]: {
        width: "100%",
        height: "60px"
    },
    "&:hover": {
        boxShadow: "0px 6px 10px 0px rgba(0,0,0,0.14),0px 1px 18px 0px rgba(0,0,0,0.12),0px 3px 5px 0px rgba(0,0,0,0.2)",
        background: "rgb(255, 200, 0)"
    }
}))

export const RegisterButtonSmallMenuStyled = styled(RegisterButtonStyled)(({ theme }) => ({
    marginLeft: "0"
}))

export default RegisterButtonStyled