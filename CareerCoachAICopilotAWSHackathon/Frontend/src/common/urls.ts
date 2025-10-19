import { SYSTEM_CONSTANTS } from './constant';

const API_URL = SYSTEM_CONSTANTS.API_URL;
export const URLS = {
  API_GOOGLE_AUTH: API_URL + '/v1/auth/google',
  API_COMPLETE_USER_PROFILE: API_URL + '/v1/ai/users/complete-profile',
  API_PROFILE_QUESTIONS: API_URL + '/v1/ai/profile/questions',
  API_PROFILE_ROADMAP: API_URL + '/v1/ai/profile/roadmap',
  API_USER_PROFILE_ME_STATE: API_URL + '/v1/users/me/state',
  API_PROFILE_DETAIL_ROADMAP: API_URL + '/v1/ai/profile/detailed-roadmap',
  API_ASSESSMENT_ROADMAP_TOPIC: API_URL + '/v1/assessments/roadmap/topic',
  API_ASSESSMENT_ROADMAP_PROGRESS: API_URL + '/v1/assessments/progress/roadmap/',
  API_ASSESSMENT_EVALUATE: API_URL + '/v1/assessment/evaluate',
};
