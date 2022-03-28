import {
  Theme,
  ToggleButtonGroup,
  ToggleButtonGroupProps,
  useTheme,
} from "@mui/material";
import { UserType } from "App";
import { primaryColour, secondaryColour, tertiaryColour } from "colours";
import React from "react";

// TODO: move this to a future User object or theme
const getSubNavBackgroundColor = (userType?: UserType) => {
  switch (userType) {
    case "student":
      return tertiaryColour[300];
    case "independent":
      return secondaryColour[300];
    case "teacher":
    case "none":
    default:
      return primaryColour[300];
  }
};

// TODO: move this to a future User object or theme
const getSubNavTextColor = (theme: Theme, userType?: UserType) => {
  switch (userType) {
    case "student":
      return theme.palette.tertiary.contrastText;
    case "independent":
      return theme.palette.secondary.contrastText;
    case "teacher":
    case "none":
    default:
      return theme.palette.primary.contrastText;
  }
};

interface SubNavProps extends ToggleButtonGroupProps {
  initialValue?: string;
  userType?: UserType;
}

const SubNav = (props: SubNavProps) => {
  const theme = useTheme();
  const [selectedValue, setSelectedValue] = React.useState(props.initialValue);

  const handleSubNavItem = (
    _event: React.MouseEvent<HTMLElement, MouseEvent>,
    newSelectedValue: string
  ) => {
    if (newSelectedValue !== null) {
      setSelectedValue(newSelectedValue);
    }
  };

  return (
    <ToggleButtonGroup
      value={selectedValue}
      exclusive
      onChange={handleSubNavItem}
      aria-label="subnav"
      sx={{
        display: "flex",
        backgroundColor: getSubNavBackgroundColor(props.userType),
        justifyContent: "center",
        alignItems: "center",
        height: 60,
        "& .MuiToggleButtonGroup-grouped": {
          textTransform: "none",
          margin: theme.spacing(2),
          height: 42,
          minWidth: 150,
          color: getSubNavTextColor(theme, props.userType),
          borderRadius: 0,
          "&:hover": {
            backgroundColor: "transparent",
            textDecoration: "underline",
          },
          "&:first-of-type, &:not(:first-of-type)": {
            borderWidth: 1,
            borderColor: getSubNavTextColor(theme, props.userType),
          },
          "&.Mui-selected": {
            color: getSubNavBackgroundColor(props.userType),
            backgroundColor: getSubNavTextColor(theme, props.userType),
          },
        },
      }}
    >
      {
        // Disable child button if its value is the same as `selectedValue`
        React.Children.map(props.children, (child) => {
          if (!React.isValidElement(child)) {
            return null;
          }

          return React.cloneElement(child, {
            disabled:
              child.props.disabled || selectedValue === child.props.value,
          });
        })
      }
    </ToggleButtonGroup>
  );
};

export default SubNav;
