import { useEffect, useState } from "react";
import { LandingPage } from "./components/LandingPage";
import { journeyNavigationMap, SYSTEM_CONSTANTS } from "./common/constant";
import { LoginPage } from "./components/LoginPage";
import { RegistrationPage } from "./components/RegistrationPage";
import { GoalSelectionPage } from "./components/GoalSelectionPage";
import { AISuggestionsPage } from "./components/AISuggestionsPage";
import { PathConfirmationPage } from "./components/PathConfirmationPage";
import { CareerDashboard } from "./components/CareerDashboard";
import { ProgressTracker } from "./components/ProgressTracker";
import { ProfilePage } from "./components/ProfilePage";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Loader from "./components/Loader";
import { useUserMeState } from "./common/services/userData";

export type Page =
  | "landing"
  | "login"
  | "registration"
  | "goal-selection"
  | "ai-suggestions"
  | "path-confirmation"
  | "dashboard"
  | "ai-chat"
  | "learning-hub"
  | "progress-tracker"
  | "profile"
  | "settings";

export interface UserData {
  // Common fields
  userType: "student" | "professional" | "";
  first_name: string;
  lastName: string;
  email: string;
  country: string;
  state: string;
  careerGoal: string;
  lookingFor: string;
  languagePreference: string;

  // Student-specific fields
  educationLevel: string;
  fieldOfStudy: string;
  academicInterests: string;
  studyDestination: string;

  // Professional-specific fields
  jobTitle: string;
  occupation: string;
  industry: string;
  yearsExperience: string;
  coreSkills: string;

  // Legacy fields
  highestStudy: string;
  selectedGoal: string;
  interest: string;
  selectedPath?: any;
}

export default function App() {
  const token = localStorage.getItem("authToken");
  const [loading, setLoading] = useState<boolean>(true);
  const [currentPage, setCurrentPage] = useState<Page>("landing");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const [userData, setUserData] = useState<UserData>({
    userType: "",
    first_name: "",
    lastName: "",
    email: "",
    country: "",
    state: "",
    careerGoal: "",
    lookingFor: "",
    languagePreference: "",
    educationLevel: "",
    fieldOfStudy: "",
    academicInterests: "",
    studyDestination: "",
    jobTitle: "",
    occupation: "",
    industry: "",
    yearsExperience: "",
    coreSkills: "",
    highestStudy: "",
    selectedGoal: "",
    interest: "",
  });
  const [careerPaths, setCareerPaths] = useState([]);
  const [detailRoadmap, setDetailRoadmap] = useState<any | null>(null);
  const [stateData, setStateData] = useState<any | null>(null);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "instant" });
  }, [currentPage]);

  useEffect(() => {
    setIsAuthenticated(token ? true : false);
  }, [token]);

  useEffect(() => {
    if (token) {
      useUserMeState()
        .then((res) => {
          if (res && res.success) {
            updateStateData(res.data);
            updateUserData(res.data.user);
            // Parse roadmap data
            if (res.data.current_data?.roadmap) {
              let data =
                JSON.parse(res.data.current_data.roadmap).careerPaths || [];

              // Add `id` to each career path based on the title
              data = data.map((career: any) => {
                const id = career.title.toLowerCase().replace(/\s+/g, "-");
                return { ...career, id };
              });

              // Update state or pass it further
              updateCareerPaths(data || []);
            }

            setLoading(false);
            setIsAuthenticated(true);
            const stage = res.data.journey_stage;
            const nextRoute = journeyNavigationMap[stage];
            if (nextRoute) {
              setCurrentPage(nextRoute);
            } else {
              console.warn("Unknown journey stage:", stage);
              setCurrentPage("registration");
            }
          }
        })
        .catch((err) => {
          setLoading(false);
          setIsAuthenticated(false);
          setCurrentPage("landing");
          console.error(err);
        });
    } else {
      setLoading(false);
      setIsAuthenticated(false);
      setCurrentPage("landing");
    }
  }, []);

  useEffect(() => {
    // Mark that the tab is active
    sessionStorage.setItem("tabActive", "true");

    const handleUnload = (event: BeforeUnloadEvent) => {
      // If sessionStorage key exists, it means page is reloading
      if (!sessionStorage.getItem("tabActive")) {
        localStorage.clear(); // Clear localStorage on tab close
      }
      // Remove the flag regardless
      sessionStorage.removeItem("tabActive");
    };

    // Fires on tab close or page reload
    window.addEventListener("beforeunload", handleUnload);

    return () => {
      window.removeEventListener("beforeunload", handleUnload);
    };
  }, []);

  const navigateTo = (page: Page) => {
    setCurrentPage(page);
  };

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentPage("landing");
    localStorage.removeItem("authToken");
  };

  const updateUserData = (newData: Partial<UserData>) => {
    setUserData((prev) => ({ ...prev, ...newData }));
  };

  const updateCareerPaths = (newData: any) => {
    setCareerPaths(newData);
  };

  const updateDetailRoadmap = (newData: any) => {
    setDetailRoadmap(newData);
  };

  const updateStateData = (newData: any) => {
    setStateData(newData);
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case "landing":
        return (
          <LandingPage
            onNavigate={navigateTo}
            isAuthenticated={isAuthenticated}
          />
        );
      case "login":
        return (
          <LoginPage
            onNavigate={navigateTo}
            onLogin={handleLogin}
            updateStateData={updateStateData}
            updateUserData={updateUserData}
          />
        );
      case "registration":
        return (
          <RegistrationPage
            onNavigate={navigateTo}
            userData={userData}
            // googleData={googleData}
            updateStateData={updateStateData}
            updateUserData={updateUserData}
            isAuthenticated={isAuthenticated}
          />
        );
      case "goal-selection":
        return (
          <GoalSelectionPage
            onLogout={handleLogout}
            onNavigate={navigateTo}
            userData={userData}
            updateUserData={updateUserData}
            updateCareerPaths={updateCareerPaths}
          />
        );
      case "ai-suggestions":
        return (
          <AISuggestionsPage
            onLogout={handleLogout}
            onNavigate={navigateTo}
            userData={userData}
            careerPaths={careerPaths}
            updateUserData={updateUserData}
          />
        );
      case "path-confirmation":
        return (
          <PathConfirmationPage
            onNavigate={navigateTo}
            userData={userData}
            updateUserData={updateUserData}
          />
        );
      case "dashboard":
        return (
          <CareerDashboard
            onNavigate={navigateTo}
            userData={userData}
            isAuthenticated={isAuthenticated}
            onLogout={handleLogout}
            detailRoadmap={detailRoadmap}
            updateDetailRoadmap={updateDetailRoadmap}
          />
        );
      case "progress-tracker":
        return (
          <ProgressTracker
            onNavigate={navigateTo}
            userData={userData}
            isAuthenticated={isAuthenticated}
            onLogout={handleLogout}
            detailRoadmap={detailRoadmap}
            updateDetailRoadmap={updateDetailRoadmap}
          />
        );
      case "profile":
        return (
          <ProfilePage
            onNavigate={navigateTo}
            userData={userData}
            updateUserData={updateUserData}
            isAuthenticated={isAuthenticated}
            onLogout={handleLogout}
            stateData={stateData}
          />
        );
      default:
        return (
          <LandingPage
            onNavigate={navigateTo}
            isAuthenticated={isAuthenticated}
          />
        );
    }
  };

  if (loading) {
    return <Loader />;
  }

  return (
    <GoogleOAuthProvider clientId={SYSTEM_CONSTANTS.GOOGLE_CLIENT_ID}>
      <ToastContainer
        hideProgressBar={true}
        autoClose={2500}
        position="top-center"
        theme="light"
      />
      <div className="min-h-screen bg-background">{renderCurrentPage()}</div>
      <div id="global-loader"></div>
    </GoogleOAuthProvider>
  );
}
