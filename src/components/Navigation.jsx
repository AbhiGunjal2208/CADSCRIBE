import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { Sun, Moon, LogOut, User } from 'lucide-react';

export const Navigation = () => {
  const { theme, toggleTheme } = useTheme();
  const { isAuthenticated, user, logout } = useAuth();
  const location = useLocation();

  const isWorkspacePage = location.pathname.startsWith('/workspace');
  const isProfilePage = location.pathname === '/profile';
  const showHorizontalNav = ['/', '/features', '/about'].includes(location.pathname);

  return (
    <>
      {/* Only show horizontal navigation on landing, features, and about pages */}
      {showHorizontalNav && (
        <nav className="border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="container mx-auto px-4 py-3">
            <div className="flex items-center justify-between">
              <Link to="/" className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                CADSCRIBE
              </Link>

              <div className="hidden md:flex items-center space-x-6">
                <Link 
                  to="/features" 
                  className="text-foreground hover:text-primary transition-colors"
                >
                  Features
                </Link>
                <Link 
                  to="/about" 
                  className="text-foreground hover:text-primary transition-colors"
                >
                  About
                </Link>
              </div>

              <div className="flex items-center space-x-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleTheme}
                  className="h-9 w-9"
                >
                  {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                </Button>

                {isAuthenticated ? (
                  <div className="flex items-center space-x-2">
                    <Link to="/workspace">
                      <Button variant="outline" size="sm">
                        Workspace
                      </Button>
                    </Link>
                    <Link to="/profile">
                      <Button variant="ghost" size="icon" className="h-9 w-9">
                        <User className="h-4 w-4" />
                      </Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={logout}
                      className="h-9 w-9"
                    >
                      <LogOut className="h-4 w-4" />
                    </Button>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <Link to="/auth/login">
                      <Button variant="ghost" size="sm">
                        Login
                      </Button>
                    </Link>
                    <Link to="/auth/signup">
                      <Button size="sm">
                        Sign Up
                      </Button>
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        </nav>
      )}
    </>
  );
};
