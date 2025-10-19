import { request } from '../http';
import { URLS } from '../urls';

export const useGoogleAuth = async (payload: any) => {
  return await request(URLS.API_GOOGLE_AUTH, 'POST', payload, true, true).then((res) => {
    if (res && res.access_token) {
      localStorage.setItem('authToken', res.access_token);
    }
    return Promise.resolve(res);
  })
};

export const useCompleteProfile = async (payload: any) => {
  return await request(URLS.API_COMPLETE_USER_PROFILE, 'POST', payload, true, true);
};

export const useProfileQuestions = async () => {
  return await request(URLS.API_PROFILE_QUESTIONS, 'POST', {}, true, true);
};

export const useProfileRoadMap = async (payload: any) => {
  const response = await request(URLS.API_PROFILE_ROADMAP, 'POST', payload, true, true, {
    useDataAsParams: true,
  });

  if (response?.data?.careerPaths && Array.isArray(response.data.careerPaths)) {
    response.data.careerPaths = response.data.careerPaths.map((career: any) => {
      const id = career.title.toLowerCase().replace(/\s+/g, '-');
      return { ...career, id };
    });
  }

  return response;
};

export const useUserMeState = async () => {
  return await request(URLS.API_USER_PROFILE_ME_STATE, 'GET', {}, true);
};

export const useProfileDetailRoadmap = async (payload: any) => {
  return await request(URLS.API_PROFILE_DETAIL_ROADMAP, 'POST', JSON.stringify(payload), true, true);
};

export const useAssessmentRoadmapTopic = async (payload: any) => {
  return await request(URLS.API_ASSESSMENT_ROADMAP_TOPIC, 'POST', JSON.stringify(payload), true, true);
};

export const useAssessmentEvaluate = async (responses: any, assessmentId: string) => {
  const data = { 
    responses: responses,
    assessment_id: assessmentId
  };
  return await request(URLS.API_ASSESSMENT_EVALUATE, 'POST', JSON.stringify(data), true, true);
};

export const useAssessmentProgress = async (id: string) => {
  return await request(URLS.API_ASSESSMENT_ROADMAP_PROGRESS + id, 'GET', {}, true, true);
};