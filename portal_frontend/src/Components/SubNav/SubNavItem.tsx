import { Button, ButtonProps, styled } from "@mui/material";

// const SubNavItem = styled(
//   ({ ...otherProps }) => <Button {...otherProps} />,
//   {}
// )(({ theme }) => ({
//   // color: theme.palette.secondary.contrastText,
//   borderColor: theme.palette.secondary.contrastText,
//   borderRadius: 0,
// }));

const SubNavItem = (props: ButtonProps) => (
  <Button
    variant="outlined"
    sx={{
      color: "secondary.contrastText",
      borderColor: "secondary.contrastText",
      borderRadius: 0,
      "&:hover": {
        borderColor: "secondary.contrastText",
      },
    }}
    {...props}
  >
    {props.children}
  </Button>
);

export default SubNavItem;
