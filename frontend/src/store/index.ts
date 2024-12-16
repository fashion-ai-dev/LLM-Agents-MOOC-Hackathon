import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

import { env } from '@/config/env';

import { createChatSlice } from './slices/chatSlice';
import { createSocketSlice } from './slices/socketSlice';
import { Store } from './Store';

export const useStore = create<Store>()(
  devtools(
    immer((...params) => ({
      chat: createChatSlice(...params),
      socket: createSocketSlice(...params),
    })),
    {
      name: 'Global Store',
      store: 'global',
      enabled: env.DEV,
    },
  ),
);
