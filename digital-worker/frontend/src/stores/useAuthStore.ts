import { create } from 'zustand';

interface AuthState {
  currentUser: {
    user_id: string;
    username: string;
    real_name: string;
    role: string;
    avatar?: string;
  } | null;
  token: string | null;
  isLoggedIn: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  currentUser: {
    user_id: 'USER_0001',
    username: 'admin',
    real_name: '管理员',
    role: 'admin',
  },
  token: localStorage.getItem('auth_token') || 'mock_token_abc123',
  isLoggedIn: true,

  login: async (username: string, _password: string) => {
    // Mock login
    const mockToken = 'mock_token_' + Math.random().toString(36).substring(2);
    localStorage.setItem('auth_token', mockToken);
    set({
      currentUser: {
        user_id: 'USER_0001',
        username,
        real_name: username === 'admin' ? '管理员' : username,
        role: 'admin',
      },
      token: mockToken,
      isLoggedIn: true,
    });
    return true;
  },

  logout: () => {
    localStorage.removeItem('auth_token');
    set({
      currentUser: null,
      token: null,
      isLoggedIn: false,
    });
  },
}));
