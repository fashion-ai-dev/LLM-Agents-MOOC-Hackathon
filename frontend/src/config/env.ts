export const env = {
  PROD: import.meta.env.PROD,
  DEV: import.meta.env.DEV,
  MODE: import.meta.env.MODE,
  SOCKET_URL: import.meta.env.VITE_SOCKET_URL as string | undefined,
};
