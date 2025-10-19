import { ArrowLeft, User } from "lucide-react";
import type { Page, UserData } from "../App";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface ProfilePageProps {
  onNavigate: (page: Page) => void;
  userData: UserData;
  updateUserData: (data: Partial<UserData>) => void;
  isAuthenticated?: boolean;
  onLogout?: () => void;
  stateData: any;
}

export function ProfilePage({ onNavigate, stateData }: ProfilePageProps) {
  const registration = stateData?.current_data?.registration;
  const user = stateData?.user;
  const mergedData = { ...registration, ...user };

  const getFormFields = () => {
    const excludeKeys = [
      "ai_insights",
      "skill_gaps",
      "recommendations",
      "tags",
      "is_complete",
      "created_at",
      "updated_at",
      "last_login_at",
      "source",
      "id",
      "is_active",
      "status",
      "is_verified",
      "profile_version",
      "profile_summary",
      "auth_provider",
      "is_current",
      "role",
      "full_name",
    ];

    // Define the fields you want to appear first in order
    const customOrder = ["first_name", "last_name", "email"];

    if (!mergedData || typeof mergedData !== "object") return null;

    return Object.entries(mergedData)
      .filter(([key]) => !excludeKeys.includes(key))
      .sort(([a], [b]) => {
        const aIndex = customOrder.indexOf(a);
        const bIndex = customOrder.indexOf(b);

        if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex; // both in custom order
        if (aIndex !== -1) return -1; // a has priority
        if (bIndex !== -1) return 1; // b has priority

        return a.localeCompare(b); // fallback to alphabetical
      })
      .map(([key, value]) => (
        <div className="col-md-6" key={key}>
          <label className="form-label font-semibold mb-0">
            {key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}:
          </label>
          <p className="form-control-plaintext text-capitalize">
            {value && value.toString() !== "" ? value.toString() : "-"}
          </p>
        </div>
      ));
  };

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: "var(--background)" }}
    >
      {/* Header */}
      <header
        className="bg-white border-bottom sticky-top"
        style={{ boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}
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
                Anblicks Career Coach
              </span>
            </div>
            <button
              className="btn btn-outline-secondary"
              onClick={() => onNavigate("dashboard")}
            >
              <ArrowLeft className="me-2" size={16} />
              Dashboard
            </button>
          </div>
        </div>
      </header>

      <div className="container py-5" style={{ maxWidth: "900px" }}>
        {/* Profile Card */}
        <div className="card shadow-sm mb-4">
          <div
            className="card-body p-4 text-center"
            style={{ backgroundColor: "rgba(10, 78, 193, 0.05)" }}
          >
            <div className="position-relative d-inline-block mb-3">
              <div
                className="text-uppercase rounded-circle d-flex align-items-center justify-content-center mx-auto text-white fw-bold"
                style={{
                  width: "100px",
                  height: "100px",
                  background:
                    "linear-gradient(135deg, var(--primary), var(--accent))",
                  fontSize: "2rem",
                }}
              >
                {mergedData.first_name?.[0]}
                {mergedData.last_name?.[0]}
              </div>
            </div>
            <h4 className="mb-1">
              {mergedData.first_name} {mergedData.last_name}
            </h4>
            <p className="text-muted mb-3">{mergedData.email}</p>
            <p className="font-semibold text-muted">
              {stateData?.current_data?.registration?.profile_summary}
            </p>
          </div>
        </div>

        {/* Profile Information */}
        <div className="card shadow-sm mb-4">
          <div className="card-header">
            <div className="d-flex">
              <User size={20} className="me-2" />
              <h5 className="mb-0">Personal Information</h5>
            </div>
          </div>
          <div className="card-body">
            <div className="row g-3">{getFormFields()}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
