import type { Page } from "../App";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface AppFooterProps {
  onNavigate: (page: Page) => void;
  isAuthenticated?: boolean;
}

export function Footer({ onNavigate, isAuthenticated }: AppFooterProps) {
  return (
    <footer
      className="bg-white border-top mt-auto"
      style={{ borderColor: "var(--border)" }}
    >
      <div className="container py-4">
        <div className="row align-items-center">
          <div className="col-md-6 text-center text-md-start mb-3 mb-md-0">
            <div
              className="d-flex align-items-center justify-content-center justify-content-md-start gap-2 mb-2"
              style={{ cursor: "pointer" }}
              onClick={() =>
                onNavigate((!isAuthenticated ? "landing" : "dashboard") as Page)
              }
            >
              <div className="flex items-center justify-center">
                <ImageWithFallback
                  src="assets/logo.svg"
                  alt="Anblicks AI Career Coaching"
                />
              </div>
              <span className="fw-semibold">Anblicks Career Coach</span>
            </div>
          </div>
          <div className="col-md-6">
            <div className="d-flex justify-content-center justify-content-md-end gap-4 flex-wrap">
              <p className="text-muted small mb-0">
                &copy; {new Date().getFullYear()} Anblicks. All rights reserved.
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
