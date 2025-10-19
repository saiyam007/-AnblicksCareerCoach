import React, { useState } from "react";
import { Briefcase, GraduationCap, CheckCircle, Sparkles } from "lucide-react";
import type { Page, UserData } from "../App";
import { Footer } from "./Footer";
import { GoogleLogin } from "@react-oauth/google";
import useLoader from "../hooks/useLoading";
import {
  useCompleteProfile,
  useGoogleAuth,
  useUserMeState,
} from "../common/services/userData";
import { journeyNavigationMap } from "../common/constant";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface RegistrationPageProps {
  onNavigate: (page: Page) => void;
  userData: UserData;
  updateUserData: (data: Partial<UserData>) => void;
  updateStateData: (data: any) => void;
  isAuthenticated: boolean;
}

export function RegistrationPage({
  onNavigate,
  userData,
  updateUserData,
  updateStateData,
  isAuthenticated,
}: RegistrationPageProps) {
  const [currentStep, setCurrentStep] = useState(isAuthenticated ? 2 : 1);
  const [formData, setFormData] = useState(userData);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [showMainLoader, hideMainLoader] = useLoader();

  const handleInputChange = (field: keyof UserData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }));
    }
  };

  const handleUserTypeChange = (type: "student" | "professional") => {
    setFormData((prev) => ({ ...prev, userType: type }));
    setErrors({});
  };

  const validateStep1 = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.first_name) newErrors.first_name = "First name is required";
    if (!formData.lastName) newErrors.lastName = "Last name is required";
    if (!formData.email) newErrors.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(formData.email))
      newErrors.email = "Email is invalid";
    if (!formData.country) newErrors.country = "Country is required";
    if (!formData.state) newErrors.state = "State is required";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.userType)
      newErrors.userType = "Please select Student or Professional";
    if (!formData.careerGoal)
      newErrors.careerGoal = "Future aspiration is required";
    if (!formData.lookingFor) newErrors.lookingFor = "This field is required";
    if (!formData.languagePreference)
      newErrors.languagePreference = "Language preference is required";

    // Student-specific validations
    if (formData.userType === "student") {
      if (!formData.educationLevel)
        newErrors.educationLevel = "Education level is required";
      if (!formData.fieldOfStudy)
        newErrors.fieldOfStudy = "Field of study is required";
      if (!formData.academicInterests)
        newErrors.academicInterests = "Academic interests are required";
      if (!formData.studyDestination)
        newErrors.studyDestination = "Study destination is required";
    }

    // Professional-specific validations
    if (formData.userType === "professional") {
      if (!formData.jobTitle) newErrors.jobTitle = "Job title is required";
      if (!formData.occupation) newErrors.occupation = "Occupation is required";
      if (!formData.industry) newErrors.industry = "Industry is required";
      if (!formData.yearsExperience)
        newErrors.yearsExperience = "Years of experience is required";
      if (!formData.coreSkills)
        newErrors.coreSkills = "Core skills are required";
    }

    if (!acceptedTerms)
      newErrors.terms = "You must accept the terms and privacy policy";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateStep2()) {
      let payload: any = { ...formData };
      if (formData.userType === "student") {
        const relevantKeys = [
          "userType",
          "careerGoal",
          "lookingFor",
          "languagePreference",
          "educationLevel",
          "fieldOfStudy",
          "academicInterests",
          "studyDestination",
          "country",
          "state",
        ];
        payload = Object.fromEntries(
          Object.entries(payload).filter(([key]) => relevantKeys.includes(key))
        );
      } else {
        const relevantKeys = [
          "userType",
          "careerGoal",
          "lookingFor",
          "languagePreference",
          "jobTitle",
          "occupation",
          "industry",
          "yearsExperience",
          "coreSkills",
          "country",
          "state",
        ];
        payload = Object.fromEntries(
          Object.entries(payload).filter(([key]) => relevantKeys.includes(key))
        );
      }
      showMainLoader();
      useCompleteProfile(payload)
        .then((res) => {
          if (res && res.success) {
            useUserMeState()
              .then((res) => {
                if (res && res.success) {
                  updateStateData(res.data);
                  updateUserData(res.data.user);
                  onNavigate("goal-selection");
                }
                hideMainLoader();
              })
              .catch((err) => {
                hideMainLoader();
                console.error(err);
              });
          }
        })
        .catch((err) => {
          hideMainLoader();
          console.error(err);
        });
    }
  };

  return (
    <div
      className="min-h-screen d-flex flex-column"
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
              <span className="text-xl font-semibold text-foreground">Anblicks Career Coach</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-grow-1">
        <div className="container-fluid h-100">
          <div className="row h-100 g-0">
            {/* Left Panel - Motivational Quote */}
            <div
              className="col-lg-6 d-none d-lg-flex align-items-center justify-content-center p-5"
              style={{
                background:
                  "linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%)",
                minHeight: "600px",
              }}
            >
              <div
                className="text-white text-center"
                style={{ maxWidth: "500px" }}
              >
                <Sparkles size={64} className="mb-4" style={{ opacity: 0.9 }} />
                <h1 className="display-4 fw-bold mb-4">
                  Your Journey Starts Here
                </h1>
                <p className="fs-5 mb-4" style={{ opacity: 0.9 }}>
                  "The future belongs to those who believe in the beauty of
                  their dreams."
                </p>
                <p className="fs-6" style={{ opacity: 0.8 }}>
                  — Eleanor Roosevelt
                </p>
                <div className="mt-5 pt-5">
                  <div className="d-flex justify-content-center gap-4">
                    <div className="text-center">
                      <h3 className="fw-bold">1K+</h3>
                      <p className="small mb-0">Career Paths</p>
                    </div>
                    <div className="text-center">
                      <h3 className="fw-bold">5K+</h3>
                      <p className="small mb-0">Success Stories</p>
                    </div>
                    <div className="text-center">
                      <h3 className="fw-bold">24/7</h3>
                      <p className="small mb-0">AI Support</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Panel - Form */}
            <div className="col-lg-6 d-flex align-items-center justify-content-center p-4">
              <div style={{ maxWidth: "600px", width: "100%" }}>
                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <span className="small fw-semibold">
                      Step {currentStep} of 2
                    </span>
                    <span className="small text-muted">
                      {currentStep === 1 ? "Account Setup" : "Profile Details"}
                    </span>
                  </div>
                  <div
                    className="progress"
                    style={{ height: "8px", borderRadius: "50px" }}
                  >
                    <div
                      className="progress-bar"
                      style={{
                        width: `${(currentStep / 2) * 100}%`,
                        backgroundColor: "var(--primary)",
                        borderRadius: "50px",
                      }}
                    ></div>
                  </div>
                </div>

                {/* Step 1: Login & Basic Info */}
                {currentStep === 1 && (
                  <div className="card shadow-sm border-0">
                    <div className="card-body p-4">
                      <h3 className="fw-bold mb-3">Create Your Account</h3>
                      <p className="text-muted mb-4">
                        Let's get started with your career journey
                      </p>

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
                                        updateStateData(res.data);
                                        updateUserData(res.data.user);
                                        const stage = res.data.journey_stage;
                                        const nextRoute =
                                          journeyNavigationMap[stage];
                                        if (nextRoute === "registration") {
                                          setCurrentStep(2);
                                          hideMainLoader?.();
                                          return;
                                        }
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
                )}

                {/* Step 2: User Type & Details */}
                {currentStep === 2 && (
                  <div className="card shadow-sm border-0">
                    <div className="card-body p-4">
                      <h3 className="fw-bold mb-3">Complete Your Profile</h3>
                      <p className="text-muted mb-4">
                        Tell us about yourself to get personalized guidance
                      </p>

                      <form onSubmit={handleSubmit}>
                        {/* User Type Selection */}
                        <div className="mb-4">
                          <label className="form-label fw-semibold">
                            Are you a Student or Professional? *
                          </label>
                          <div className="row g-3">
                            <div className="col-6">
                              <div
                                className={`card h-100 ${
                                  formData.userType === "student"
                                    ? "border-primary"
                                    : ""
                                }`}
                                style={{
                                  cursor: "pointer",
                                  backgroundColor:
                                    formData.userType === "student"
                                      ? "rgba(10, 78, 193, 0.05)"
                                      : "white",
                                  borderWidth: "2px",
                                }}
                                onClick={() => handleUserTypeChange("student")}
                              >
                                <div className="card-body text-center py-3">
                                  <div className="mb-2 d-flex justify-content-center align-items-center">
                                    <GraduationCap
                                      size={32}
                                      style={{ color: "var(--primary)" }}
                                    />
                                  </div>
                                  <h6 className="card-title mb-1">Student</h6>
                                  <p className="card-text text-muted small mb-2">
                                    Pursuing education
                                  </p>
                                  <div className="form-check d-flex justify-content-center">
                                    <input
                                      className="form-check-input"
                                      type="radio"
                                      name="userType"
                                      checked={formData.userType === "student"}
                                      onChange={() =>
                                        handleUserTypeChange("student")
                                      }
                                    />
                                  </div>
                                </div>
                              </div>
                            </div>
                            <div className="col-6">
                              <div
                                className={`card h-100 ${
                                  formData.userType === "professional"
                                    ? "border-primary"
                                    : ""
                                }`}
                                style={{
                                  cursor: "pointer",
                                  backgroundColor:
                                    formData.userType === "professional"
                                      ? "rgba(10, 78, 193, 0.05)"
                                      : "white",
                                  borderWidth: "2px",
                                }}
                                onClick={() =>
                                  handleUserTypeChange("professional")
                                }
                              >
                                <div className="card-body text-center py-3">
                                  <div className="mb-2 d-flex justify-content-center align-items-center">
                                    <Briefcase
                                      size={32}
                                      style={{ color: "var(--primary)" }}
                                    />
                                  </div>
                                  <h6 className="card-title mb-1">
                                    Professional
                                  </h6>
                                  <p className="card-text text-muted small mb-2">
                                    Working professional
                                  </p>
                                  <div className="form-check d-flex justify-content-center">
                                    <input
                                      className="form-check-input"
                                      type="radio"
                                      name="userType"
                                      checked={
                                        formData.userType === "professional"
                                      }
                                      onChange={() =>
                                        handleUserTypeChange("professional")
                                      }
                                    />
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                          {errors.userType && (
                            <div className="text-danger small mt-2">
                              {errors.userType}
                            </div>
                          )}
                        </div>

                        {/* Personal Information */}
                        <div className="mb-4">
                          <h6
                            className="fw-semibold mb-3"
                            style={{ color: "var(--primary)" }}
                          >
                            Personal Information
                          </h6>
                          <div className="row g-3">
                            <div className="col-12">
                              <label className="form-label">
                                Future Aspiration / Career Goal *
                              </label>
                              <input
                                type="text"
                                className={`form-control ${
                                  errors.careerGoal ? "is-invalid" : ""
                                }`}
                                value={formData.careerGoal}
                                onChange={(e) =>
                                  handleInputChange(
                                    "careerGoal",
                                    e.target.value
                                  )
                                }
                                placeholder="e.g., Data Scientist, Product Manager, etc."
                              />
                              {errors.careerGoal && (
                                <div className="invalid-feedback">
                                  {errors.careerGoal}
                                </div>
                              )}
                            </div>
                            <div className="col-md-6">
                              <label className="form-label">
                                Looking For *
                              </label>
                              <select
                                className={`form-select ${
                                  errors.lookingFor ? "is-invalid" : ""
                                }`}
                                value={formData.lookingFor}
                                onChange={(e) =>
                                  handleInputChange(
                                    "lookingFor",
                                    e.target.value
                                  )
                                }
                              >
                                <option value="">Select</option>
                                <option value="Career Path Exploration">
                                  Career Path Exploration
                                </option>
                                <option value="Job Search">Job Search</option>
                                <option value="Higher Education">
                                  Higher Education
                                </option>
                                <option value="International Opportunities">
                                  International Opportunities
                                </option>
                                <option value="Skill Development">
                                  Skill Development
                                </option>
                                <option value="Career Transition">
                                  Career Transition
                                </option>
                              </select>
                              {errors.lookingFor && (
                                <div className="invalid-feedback">
                                  {errors.lookingFor}
                                </div>
                              )}
                            </div>
                            <div className="col-md-6">
                              <label className="form-label">
                                Language Preference *
                              </label>
                              <select
                                className={`form-select ${
                                  errors.languagePreference ? "is-invalid" : ""
                                }`}
                                value={formData.languagePreference}
                                onChange={(e) =>
                                  handleInputChange(
                                    "languagePreference",
                                    e.target.value
                                  )
                                }
                              >
                                <option value="">Select Language</option>
                                <option value="English">English</option>
                                <option value="Spanish">Spanish</option>
                                <option value="French">French</option>
                                <option value="German">German</option>
                                <option value="Chinese">Chinese</option>
                                <option value="Hindi">Hindi</option>
                                <option value="Arabic">Arabic</option>
                              </select>
                              {errors.languagePreference && (
                                <div className="invalid-feedback">
                                  {errors.languagePreference}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Student-specific fields */}
                        {formData.userType === "student" && (
                          <div className="mb-4">
                            <h6
                              className="fw-semibold mb-3"
                              style={{ color: "var(--accent)" }}
                            >
                              Student Information
                            </h6>
                            <div className="row g-3">
                              <div className="col-md-6">
                                <label className="form-label">
                                  Current Education Level *
                                </label>
                                <select
                                  className={`form-select ${
                                    errors.educationLevel ? "is-invalid" : ""
                                  }`}
                                  value={formData.educationLevel}
                                  onChange={(e) =>
                                    handleInputChange(
                                      "educationLevel",
                                      e.target.value
                                    )
                                  }
                                >
                                  <option value="">Select</option>
                                  <option value="High School">
                                    High School
                                  </option>
                                  <option value="Associate Degree">
                                    Associate Degree
                                  </option>
                                  <option value="Bachelor's Degree">
                                    Bachelor's Degree
                                  </option>
                                  <option value="Master's Degree">
                                    Master's Degree
                                  </option>
                                  <option value="Doctorate">Doctorate</option>
                                </select>
                                {errors.educationLevel && (
                                  <div className="invalid-feedback">
                                    {errors.educationLevel}
                                  </div>
                                )}
                              </div>
                              <div className="col-md-6">
                                <label className="form-label">
                                  Field of Study / Major *
                                </label>
                                <input
                                  type="text"
                                  className={`form-control ${
                                    errors.fieldOfStudy ? "is-invalid" : ""
                                  }`}
                                  value={formData.fieldOfStudy}
                                  onChange={(e) =>
                                    handleInputChange(
                                      "fieldOfStudy",
                                      e.target.value
                                    )
                                  }
                                  placeholder="e.g., Computer Science"
                                />
                                {errors.fieldOfStudy && (
                                  <div className="invalid-feedback">
                                    {errors.fieldOfStudy}
                                  </div>
                                )}
                              </div>
                              <div className="col-12">
                                <label className="form-label">
                                  Academic Interests *
                                </label>
                                <textarea
                                  className={`form-control ${
                                    errors.academicInterests ? "is-invalid" : ""
                                  }`}
                                  rows={3}
                                  value={formData.academicInterests}
                                  onChange={(e) =>
                                    handleInputChange(
                                      "academicInterests",
                                      e.target.value
                                    )
                                  }
                                  placeholder="Tell us about your academic interests..."
                                />
                                {errors.academicInterests && (
                                  <div className="invalid-feedback">
                                    {errors.academicInterests}
                                  </div>
                                )}
                              </div>
                              <div className="col-12">
                                <label className="form-label">
                                  Preferred Study Destination *
                                </label>
                                <input
                                  type="text"
                                  className={`form-control ${
                                    errors.studyDestination ? "is-invalid" : ""
                                  }`}
                                  value={formData.studyDestination}
                                  onChange={(e) =>
                                    handleInputChange(
                                      "studyDestination",
                                      e.target.value
                                    )
                                  }
                                  placeholder="e.g., United States, United Kingdom"
                                />
                                {errors.studyDestination && (
                                  <div className="invalid-feedback">
                                    {errors.studyDestination}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Professional-specific fields */}
                        {formData.userType === "professional" && (
                          <div className="mb-4">
                            <h6
                              className="fw-semibold mb-3"
                              style={{ color: "var(--accent)" }}
                            >
                              Professional Information
                            </h6>
                            <div className="row g-3">
                              <div className="col-md-6">
                                <label className="form-label">
                                  Current Job Title *
                                </label>
                                <input
                                  type="text"
                                  className={`form-control ${
                                    errors.jobTitle ? "is-invalid" : ""
                                  }`}
                                  value={formData.jobTitle}
                                  onChange={(e) =>
                                    handleInputChange(
                                      "jobTitle",
                                      e.target.value
                                    )
                                  }
                                  placeholder="e.g., Software Engineer"
                                />
                                {errors.jobTitle && (
                                  <div className="invalid-feedback">
                                    {errors.jobTitle}
                                  </div>
                                )}
                              </div>
                              <div className="col-md-6">
                                <label className="form-label">
                                  Occupation *
                                </label>
                                <input
                                  type="text"
                                  className={`form-control ${
                                    errors.occupation ? "is-invalid" : ""
                                  }`}
                                  value={formData.occupation}
                                  onChange={(e) =>
                                    handleInputChange(
                                      "occupation",
                                      e.target.value
                                    )
                                  }
                                  placeholder="e.g., Developer"
                                />
                                {errors.occupation && (
                                  <div className="invalid-feedback">
                                    {errors.occupation}
                                  </div>
                                )}
                              </div>
                              <div className="col-md-6">
                                <label className="form-label">
                                  Industry / Domain *
                                </label>
                                <select
                                  className={`form-select ${
                                    errors.industry ? "is-invalid" : ""
                                  }`}
                                  value={formData.industry}
                                  onChange={(e) =>
                                    handleInputChange(
                                      "industry",
                                      e.target.value
                                    )
                                  }
                                >
                                  <option value="">Select Industry</option>
                                  <option value="Technology">Technology</option>
                                  <option value="Healthcare">Healthcare</option>
                                  <option value="Finance">Finance</option>
                                  <option value="Education">Education</option>
                                  <option value="Manufacturing">
                                    Manufacturing
                                  </option>
                                  <option value="Retail">Retail</option>
                                  <option value="Consulting">Consulting</option>
                                  <option value="Media">Media</option>
                                  <option value="Other">Other</option>
                                </select>
                                {errors.industry && (
                                  <div className="invalid-feedback">
                                    {errors.industry}
                                  </div>
                                )}
                              </div>
                              <div className="col-md-6">
                                <label className="form-label">
                                  Years of Experience *
                                </label>
                                <select
                                  className={`form-select ${
                                    errors.yearsExperience ? "is-invalid" : ""
                                  }`}
                                  value={formData.yearsExperience}
                                  onChange={(e) =>
                                    handleInputChange(
                                      "yearsExperience",
                                      e.target.value
                                    )
                                  }
                                >
                                  <option value="">Select Years</option>
                                  <option value="0-1">0-1 years</option>
                                  <option value="1-3">1-3 years</option>
                                  <option value="3-5">3-5 years</option>
                                  <option value="5-10">5-10 years</option>
                                  <option value="10+">10+ years</option>
                                </select>
                                {errors.yearsExperience && (
                                  <div className="invalid-feedback">
                                    {errors.yearsExperience}
                                  </div>
                                )}
                              </div>
                              <div className="col-12">
                                <label className="form-label">
                                  Core Skills *
                                </label>
                                <textarea
                                  className={`form-control ${
                                    errors.coreSkills ? "is-invalid" : ""
                                  }`}
                                  rows={3}
                                  value={formData.coreSkills}
                                  onChange={(e) =>
                                    handleInputChange(
                                      "coreSkills",
                                      e.target.value
                                    )
                                  }
                                  placeholder="List your core professional skills..."
                                />
                                {errors.coreSkills && (
                                  <div className="invalid-feedback">
                                    {errors.coreSkills}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        )}

                        <div className="row g-3 mb-4">
                          <div className="col-md-6">
                            <label className="form-label">Country *</label>
                            <select
                              className={`form-select ${
                                errors.country ? "is-invalid" : ""
                              }`}
                              value={formData.country}
                              onChange={(e) =>
                                handleInputChange("country", e.target.value)
                              }
                            >
                              <option value="">Select Country</option>
                              <option value="United States">
                                United States
                              </option>
                              <option value="United Kingdom">
                                United Kingdom
                              </option>
                              <option value="Canada">Canada</option>
                              <option value="Australia">Australia</option>
                              <option value="India">India</option>
                              <option value="Germany">Germany</option>
                              <option value="France">France</option>
                              <option value="Singapore">Singapore</option>
                              <option value="UAE">UAE</option>
                              <option value="Other">Other</option>
                            </select>
                            {errors.country && (
                              <div className="invalid-feedback">
                                {errors.country}
                              </div>
                            )}
                          </div>
                          <div className="col-md-6">
                            <label className="form-label">
                              State / Province *
                            </label>
                            <input
                              type="text"
                              className={`form-control ${
                                errors.state ? "is-invalid" : ""
                              }`}
                              value={formData.state}
                              onChange={(e) =>
                                handleInputChange("state", e.target.value)
                              }
                              placeholder="California"
                            />
                            {errors.state && (
                              <div className="invalid-feedback">
                                {errors.state}
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Terms and Privacy */}
                        <div className="mb-4">
                          <div className="form-check">
                            <input
                              className="form-check-input"
                              type="checkbox"
                              id="termsCheck"
                              checked={acceptedTerms}
                              onChange={(e) =>
                                setAcceptedTerms(e.target.checked)
                              }
                            />
                            <label
                              className="form-check-label small"
                              htmlFor="termsCheck"
                            >
                              I agree to the{" "}
                              <a
                                href="#"
                                onClick={(e) => {
                                  e.preventDefault();
                                  setShowTermsModal(true);
                                }}
                                style={{ color: "var(--primary)" }}
                              >
                                Terms of Service
                              </a>{" "}
                              and{" "}
                              <a
                                href="#"
                                onClick={(e) => {
                                  e.preventDefault();
                                  setShowPrivacyModal(true);
                                }}
                                style={{ color: "var(--primary)" }}
                              >
                                Privacy Policy
                              </a>
                            </label>
                          </div>
                          {errors.terms && (
                            <div className="text-danger small mt-1">
                              {errors.terms}
                            </div>
                          )}
                        </div>

                        {/* Action Buttons */}
                        <div className="d-flex gap-2">
                          <button
                            type="button"
                            onClick={() => setCurrentStep(1)}
                            className="btn btn-outline-secondary"
                            style={{ flex: "0 0 100px" }}
                          >
                            Back
                          </button>
                          <button
                            type="submit"
                            className="btn flex-fill text-white"
                            style={{ backgroundColor: "var(--primary)" }}
                          >
                            Complete Registration
                            <CheckCircle className="ms-2" size={20} />
                          </button>
                        </div>
                      </form>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Terms Modal */}
      {showTermsModal && (
        <div
          className="modal d-block"
          style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
          onClick={() => setShowTermsModal(false)}
        >
          <div
            className="modal-dialog modal-lg modal-dialog-scrollable"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-content">
              <div
                className="modal-header"
                style={{ backgroundColor: "var(--primary)", color: "white" }}
              >
                <h5 className="modal-title">Terms of Service</h5>
                <button
                  type="button"
                  className="btn-close btn-close-white"
                  onClick={() => setShowTermsModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                <h6 className="fw-bold mb-3">1. Acceptance of Terms</h6>
                <p>
                  By accessing and using Anblicks Career Coach, you accept and
                  agree to be bound by the terms and provision of this
                  agreement.
                </p>

                <h6 className="fw-bold mb-3 mt-4">2. Use License</h6>
                <p>
                  Permission is granted to temporarily use Anblicks Career Coach
                  for personal, non-commercial transitory viewing only. This is
                  the grant of a license, not a transfer of title.
                </p>

                <h6 className="fw-bold mb-3 mt-4">3. Service Description</h6>
                <p>
                  Anblicks Career Coach provides AI-powered career guidance,
                  learning resources, and personalized career path
                  recommendations. We do not guarantee specific career outcomes
                  or job placements.
                </p>

                <h6 className="fw-bold mb-3 mt-4">4. User Responsibilities</h6>
                <p>
                  You are responsible for maintaining the confidentiality of
                  your account and password. You agree to accept responsibility
                  for all activities that occur under your account.
                </p>

                <h6 className="fw-bold mb-3 mt-4">5. Intellectual Property</h6>
                <p>
                  All content, features, and functionality are owned by Anblicks
                  and are protected by international copyright, trademark, and
                  other intellectual property laws.
                </p>

                <h6 className="fw-bold mb-3 mt-4">
                  6. Limitation of Liability
                </h6>
                <p>
                  Anblicks shall not be liable for any indirect, incidental,
                  special, consequential, or punitive damages resulting from
                  your use of or inability to use the service.
                </p>

                <h6 className="fw-bold mb-3 mt-4">7. Changes to Terms</h6>
                <p>
                  We reserve the right to modify these terms at any time.
                  Continued use of the service after changes constitutes
                  acceptance of the modified terms.
                </p>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowTermsModal(false)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Privacy Policy Modal */}
      {showPrivacyModal && (
        <div
          className="modal d-block"
          style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
          onClick={() => setShowPrivacyModal(false)}
        >
          <div
            className="modal-dialog modal-lg modal-dialog-scrollable"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-content">
              <div
                className="modal-header"
                style={{ backgroundColor: "var(--accent)", color: "white" }}
              >
                <h5 className="modal-title">Privacy Policy</h5>
                <button
                  type="button"
                  className="btn-close btn-close-white"
                  onClick={() => setShowPrivacyModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                <h6 className="fw-bold mb-3">1. Information We Collect</h6>
                <p>
                  We collect information you provide directly to us, including
                  name, email address, educational background, professional
                  experience, and career aspirations.
                </p>

                <h6 className="fw-bold mb-3 mt-4">
                  2. How We Use Your Information
                </h6>
                <p>We use the information we collect to:</p>
                <ul>
                  <li>
                    Provide personalized career guidance and recommendations
                  </li>
                  <li>Improve and develop our AI algorithms</li>
                  <li>
                    Communicate with you about your account and our services
                  </li>
                  <li>Analyze usage patterns to enhance user experience</li>
                </ul>

                <h6 className="fw-bold mb-3 mt-4">3. Information Sharing</h6>
                <p>
                  We do not sell, trade, or rent your personal information to
                  third parties. We may share anonymized, aggregated data for
                  research and improvement purposes.
                </p>

                <h6 className="fw-bold mb-3 mt-4">4. Data Security</h6>
                <p>
                  We implement appropriate technical and organizational measures
                  to protect your personal information against unauthorized
                  access, alteration, disclosure, or destruction.
                </p>

                <h6 className="fw-bold mb-3 mt-4">5. Your Rights</h6>
                <p>
                  You have the right to access, update, or delete your personal
                  information at any time through your account settings or by
                  contacting us.
                </p>

                <h6 className="fw-bold mb-3 mt-4">6. Cookies and Tracking</h6>
                <p>
                  We use cookies and similar tracking technologies to improve
                  your experience, analyze usage patterns, and personalize
                  content.
                </p>

                <h6 className="fw-bold mb-3 mt-4">7. Children's Privacy</h6>
                <p>
                  Our service is not intended for users under 13 years of age.
                  We do not knowingly collect information from children under
                  13.
                </p>

                <h6 className="fw-bold mb-3 mt-4">
                  8. Changes to Privacy Policy
                </h6>
                <p>
                  We may update this privacy policy from time to time. We will
                  notify you of any changes by posting the new policy on this
                  page.
                </p>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowPrivacyModal(false)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <Footer onNavigate={onNavigate} />
    </div>
  );
}
