/**
 * useSession Hook
 * 
 * Convenient hook to access session context.
 * Re-exports useSessionContext for easier imports.
 */

import { useSessionContext } from '../contexts/SessionContext';

export const useSession = () => {
  return useSessionContext();
};

export default useSession;
