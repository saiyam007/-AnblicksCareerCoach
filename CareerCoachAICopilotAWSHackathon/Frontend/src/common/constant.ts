export const SYSTEM_CONSTANTS = {
  API_URL: import.meta.env.VITE_API_URL,
  GOOGLE_CLIENT_ID: import.meta.env.VITE_GOOGLE_CLIENT_ID,
};

export const journeyNavigationMap: any = {
  AUTHENTICATED: "registration",
  BASIC_REGISTERED: "goal-selection",
  PROFILE_COMPLETED: "goal-selection",
  CAREER_PATHS_GENERATED: "ai-suggestions",
  CAREER_PATH_SELECTED: "dashboard",
  ROADMAP_GENERATED: "dashboard",
  ROADMAP_ACTIVE: "dashboard",
  JOURNEY_COMPLETED: "dashboard",
  JOURNEY_PAUSED: "dashboard",
};