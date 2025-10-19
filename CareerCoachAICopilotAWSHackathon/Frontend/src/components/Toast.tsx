import { toast } from "react-toastify";

export const SUCCESS_TOAST = "success";
export const ERROR_TOAST = "error";
export const WARNING_TOAST = "warning";
export const INFO_TOAST = "info";

const createMarkup = (message: string) => {
  return { __html: message };
};

const Toast = (
  message: string,
  type: string,
  setting = {
    autoClose: 2500,
  }
) => {
  switch (type) {
    case "success":
      return toast.success(
        <p dangerouslySetInnerHTML={createMarkup(message)}></p>,
        setting
      );
    case "info":
      return toast.info(
        <p dangerouslySetInnerHTML={createMarkup(message)}></p>,
        setting
      );
    case "error":
      return toast.error(
        <p dangerouslySetInnerHTML={createMarkup(message)}></p>,
        setting
      );
    case "warning":
      return toast.warning(
        <p dangerouslySetInnerHTML={createMarkup(message)}></p>,
        setting
      );
    default:
      return toast.warning(<p>Not Found</p>, setting);
  }
};
export default Toast;
