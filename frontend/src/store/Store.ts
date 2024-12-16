import { StateCreator } from 'zustand';

import { ChatSlice } from './slices/chatSlice';
import { SocketSlice } from './slices/socketSlice';

export type Store = {
  chat: ChatSlice;
  socket: SocketSlice;
};

export type StoreSlice<TSlice> = StateCreator<
  Store,
  [['zustand/devtools', never], ['zustand/immer', never]],
  [],
  TSlice
>;
