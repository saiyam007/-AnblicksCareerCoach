import { LogOut, User } from "lucide-react";
import type { Page } from "../App";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface AppHeaderProps {
  onNavigate: (page: Page) => void;
  isAuthenticated?: boolean;
  onLogout?: () => void;
  title?: string;
  backButton?: {
    label: string;
    page: Page;
  };
}

export function AppHeader({
  onNavigate,
  isAuthenticated,
  onLogout,
  title,
  backButton,
}: AppHeaderProps) {
  return (
    <header
      className="bg-white border-bottom sticky-top"
      style={{ boxShadow: "0 2px 8px rgba(0,0,0,0.1)", zIndex: 50 }}
    >
      <div className="container">
        <div className="d-flex justify-content-between align-items-center py-3">
          <div
            className="d-flex align-items-center gap-2"
            style={{ cursor: "pointer" }}
            onClick={() => onNavigate("dashboard")}
          >
            <div className="flex items-center justify-center">
              <ImageWithFallback
                src="assets/logo.svg"
                alt="Anblicks AI Career Coaching"
              />
            </div>
            <span className="text-xl font-semibold text-foreground">
              {title || "Anblicks Career Coach"}
            </span>
          </div>

          <div className="d-flex align-items-center gap-2">
            {backButton && (
              <button
                className="btn btn-outline-secondary"
                onClick={() => onNavigate(backButton.page)}
              >
                {backButton.label}
              </button>
            )}

            {isAuthenticated && onLogout && (
              <>
                <button className="btn btn-outline-danger" onClick={onLogout}>
                  <LogOut size={16} className="me-2" />
                  Logout
                </button>
                <button
                  className="btn btn-outline-primary"
                  onClick={() => onNavigate("profile")}
                >
                  <User className="w-4 h-4 mr-3" />
                  Me
                </button>
              </>
            )}

            {!isAuthenticated && (
              <button
                className="btn text-white"
                style={{ backgroundColor: "var(--primary)" }}
                onClick={() => onNavigate("login")}
              >
                Login
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
