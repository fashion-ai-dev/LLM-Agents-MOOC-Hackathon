import { StoreSlice } from '../Store';

type SocketState = {
  isConnected: boolean;
};

type SocketActions = {
  setIsConnected: (value: boolean) => void;
};

export type SocketSlice = SocketState & SocketActions;

export const createSocketSlice: StoreSlice<SocketSlice> = (set) => ({
  isConnected: false,
  setIsConnected: (value) =>
    set((state) => {
      state.socket.isConnected = value;
    }),
});
