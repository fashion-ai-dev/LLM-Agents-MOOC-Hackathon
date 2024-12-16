import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';

import { useStore } from '@/store';

export function useThreadParams() {
  const [searchParams, setSearchParams] = useSearchParams();

  const { selectedUser, setSelectedUser } = useStore((state) => state.chat);

  const params = useMemo(
    () => ({
      threadId: searchParams.get('t') ?? '',
      customerId: searchParams.get('c') ?? '',
      userId: searchParams.get('u') ?? '',
    }),
    [searchParams],
  );

  const setThreadParams = useCallback(
    (threadId: string | number, customerId: string | number) => {
      if (selectedUser) {
        setSearchParams({
          t: String(threadId),
          c: String(customerId),
          u: String(selectedUser.id),
        });
      } else {
        setSearchParams({
          t: String(threadId),
          c: String(customerId),
        });
      }
    },
    [selectedUser, setSearchParams],
  );

  const clearThreadParams = useCallback(() => {
    const params = new URLSearchParams(searchParams.toString());

    params.delete('t');
    params.delete('c');
    params.delete('u');

    setSearchParams(params);
  }, [searchParams, setSearchParams]);

  return {
    params,
    selectedUser,
    setSelectedUser,
    setThreadParams,
    clearThreadParams,
  };
}
