import type { Page } from "../App";
import { useGoogleAuth, useUserMeState } from "../common/services/userData";
import { GoogleLogin } from "@react-oauth/google";
import useLoader from "../hooks/useLoading";
import { journeyNavigationMap } from "../common/constant";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface LoginPageProps {
  onNavigate: (page: Page) => void;
  onLogin: () => void;
  updateStateData: (data: any) => void;
  updateUserData: (data: any) => void;
}

export function LoginPage({
  onNavigate,
  onLogin,
  updateStateData,
  updateUserData,
}: LoginPageProps) {
  const [showMainLoader, hideMainLoader] = useLoader();

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: "var(--background)" }}
    >
      {/* Header */}
      <header
        className="bg-white border-bottom"
        style={{ boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}
      >
        <div className="container">
          <div className="d-flex justify-content-between align-items-center py-3">
            <div
              className="d-flex align-items-center gap-2"
              style={{ cursor: "pointer" }}
              onClick={() => onNavigate("landing")}
            >
              <div className="flex items-center justify-center">
                <ImageWithFallback
                  src="assets/logo.svg"
                  alt="Anblicks AI Career Coaching"
                />
              </div>
              <span className="text-xl font-semibold text-foreground">
                Anblicks Career Coach
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div
        className="d-flex align-items-center justify-content-center"
        style={{ minHeight: "calc(100vh - 80px)" }}
      >
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-md-6 col-lg-5">
              <div className="card shadow-lg border-0">
                <div className="card-body p-5">
                  {/* Logo and Title */}
                  <div className="text-center mb-4">
                    <div className="flex items-center justify-center">
                      <ImageWithFallback
                        src="assets/logo.svg"
                        alt="Anblicks AI Career Coaching"
                      />
                    </div>
                    <h2 className="fw-bold mb-2">Welcome Back</h2>
                    <p className="text-muted">
                      Sign in to continue your career journey
                    </p>
                  </div>
                  {/* Google Login Button */}
                  <div className="d-flex justify-content-center">
                    <GoogleLogin
                      shape="circle"
                      onSuccess={(credentialResponse: any) => {
                        showMainLoader();
                        useGoogleAuth({
                          id_token: credentialResponse.credential,
                        })
                          .then((res) => {
                            if (res && res.access_token) {
                              useUserMeState()
                                .then((res) => {
                                  if (res && res.success) {
                                    onLogin();
                                    updateStateData(res.data);
                                    updateUserData(res.data.user);
                                    const stage = res.data.journey_stage;
                                    const nextRoute =
                                      journeyNavigationMap[stage];
                                    if (nextRoute) {
                                      onNavigate(nextRoute);
                                      hideMainLoader?.();
                                    } else {
                                      console.warn(
                                        "Unknown journey stage:",
                                        stage
                                      );
                                      onNavigate("registration");
                                      hideMainLoader?.();
                                    }
                                  }
                                })
                                .catch((err) => {
                                  console.error(err);
                                });
                            }
                          })
                          .catch((err) => {
                            hideMainLoader();
                            console.error(err);
                          });
                      }}
                      onError={() => {
                        hideMainLoader();
                        console.log("Login Failed");
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* Terms */}
              <p className="text-center text-muted small mt-4">
                By continuing, you agree to our{" "}
                <a href="#" style={{ color: "var(--primary)" }}>
                  Terms of Service
                </a>{" "}
                and{" "}
                <a href="#" style={{ color: "var(--primary)" }}>
                  Privacy Policy
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
