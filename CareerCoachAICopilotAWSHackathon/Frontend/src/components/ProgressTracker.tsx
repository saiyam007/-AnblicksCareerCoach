import React, { useEffect, useState } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "./ui/dialog";
import { RadioGroup, RadioGroupItem } from "./ui/radio-group";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { AppHeader } from "./AppHeader";
import { Footer } from "./Footer";
import {
  TrendingUp,
  CheckCircle,
  Clock,
  Star,
  BarChart3,
  Flag,
  FileText,
  XCircle,
  AlertCircle,
  CheckCircle2,
  Info,
  BadgeInfo,
} from "lucide-react";
import type { Page, UserData } from "../App";
import {
  useAssessmentEvaluate,
  useAssessmentProgress,
  useAssessmentRoadmapTopic,
  useProfileDetailRoadmap,
} from "../common/services/userData";
import useLoader from "../hooks/useLoading";

interface ProgressTrackerProps {
  onNavigate: (page: Page) => void;
  userData: UserData;
  isAuthenticated?: boolean;
  onLogout?: () => void;
  detailRoadmap: any;
  updateDetailRoadmap: (data: any) => void;
}

export function ProgressTracker({
  onNavigate,
  userData,
  isAuthenticated,
  onLogout,
  detailRoadmap,
  updateDetailRoadmap,
}: ProgressTrackerProps) {
  const [showMainLoader, hideMainLoader] = useLoader();
  const [showAssessmentModal, setShowAssessmentModal] = useState(false);
  const [selectedMilestone, setSelectedMilestone] = useState<any | null>(null);
  const [generatedQuestions, setGeneratedQuestions] = useState<any | null>(
    null
  );
  const [assessmentAnswers, setAssessmentAnswers] = useState<any>([]);
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [showResultModal, setShowResultModal] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState<any | null>(null);
  const [assessmentProgress, setAssessmentProgress] = useState<any | null>(
    null
  );

  const passed = parseFloat(assessmentResult?.Overall) >= 60;

  useEffect(() => {
    getAssessmentProgress();
  }, []);

  useEffect(() => {
    if (showAssessmentModal && selectedMilestone) {
      const payload = {
        roadmap_id: detailRoadmap.roadmapId,
        topic_name: selectedMilestone.topic,
      };
      showMainLoader();
      useAssessmentRoadmapTopic(payload)
        .then((res) => {
          if (res && res.success) {
            setGeneratedQuestions(res.data);
            // Store assessment_id if provided in response
            if (res.data.assessment_id) {
              setAssessmentId(res.data.assessment_id);
            }
          }
          hideMainLoader();
        })
        .catch((err) => {
          hideMainLoader();
          setShowAssessmentModal(false);
          console.error(err);
        });
    } else {
      setGeneratedQuestions(null);
    }
  }, [showAssessmentModal]);

  const getAssessmentProgress = () => {
    showMainLoader();
    useAssessmentProgress(detailRoadmap?.roadmapId)
      .then((res) => {
        if (res && res.success) {
          setAssessmentProgress(res.data);
        }
        hideMainLoader();
      })
      .catch((err) => {
        hideMainLoader();
        console.error(err);
      });
  };

  const getProfileDetailRoadmap = () => {
    showMainLoader();
    const payload = {
      selectedCareerPath: {},
    };
    useProfileDetailRoadmap(payload)
      .then((res) => {
        if (res && res.success) {
          updateDetailRoadmap(res.data);
        }
        hideMainLoader();
      })
      .catch((err) => {
        hideMainLoader();
        console.error(err);
      });
  };

  const handleOpenAssessment = (topic: any) => {
    setSelectedMilestone(topic);
    setAssessmentAnswers([]);
    setShowAssessmentModal(true);
  };

  const handleAssessmentAnswerChange = (questionId: string, answer: string) => {
    setAssessmentAnswers((prev: any) => {
      const question: any = generatedQuestions?.questions?.find(
        (q: any) => q.id === questionId
      );
      if (!question) return prev;

      const updatedEntry = {
        id: question.id,
        question: question.question,
        skill: question.skill,
        difficulty: question.difficulty,
        user_answer: answer, // directly store option text or typed text
      };

      const existingIndex = prev.findIndex((a: any) => a.id === questionId);
      if (existingIndex >= 0) {
        const updated = [...prev];
        updated[existingIndex] = updatedEntry;
        return updated;
      }

      return [...prev, updatedEntry];
    });
  };

  const handleSubmitAssessment = () => {
    if (!assessmentId) {
      console.error("Assessment ID is required for evaluation");
      return;
    }

    showMainLoader();
    useAssessmentEvaluate(assessmentAnswers, assessmentId)
      .then((res) => {
        if (res && res.success) {
          setAssessmentResult(res.data);
          setShowResultModal(true);
          setShowAssessmentModal(false);
        }
        hideMainLoader();
      })
      .catch((err) => {
        hideMainLoader();
        console.error(err);
      });
  };

  const handleCloseAssessmentModal = () => {
    setShowAssessmentModal(false);
    setSelectedMilestone(null);
    setGeneratedQuestions(null);
    setAssessmentAnswers([]);
    setAssessmentId(null);
  };

  const handleCloseResultModal = () => {
    setShowResultModal(false);
    setSelectedMilestone(null);
    setAssessmentResult(null);
    setAssessmentId(null);
    getProfileDetailRoadmap();
    getAssessmentProgress();
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "Advanced":
        return "border-info";
      case "Intermediate":
        return "border-yellow-500";
      case "Beginner":
        return "border-green-500";
      default:
        return "border-gray-300";
    }
  };

  return (
    <div className="min-h-screen bg-background d-flex flex-column">
      <AppHeader
        onNavigate={onNavigate}
        isAuthenticated={isAuthenticated}
        onLogout={onLogout}
        backButton={{ label: "Dashboard", page: "dashboard" }}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <TrendingUp className="w-8 h-8 text-primary" />
            <h1 className="text-3xl font-bold text-foreground">
              Track Your Career Growth
            </h1>
          </div>
          <p className="text-xl text-muted-foreground">
            Monitor your learning milestones and celebrate your achievements on
            the path to becoming a{" "}
            {userData.selectedPath?.title || "professional"}
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground fw-semibold">
                    Overall Progress
                  </p>
                  <p className="text-2xl font-bold text-foreground">
                    {assessmentProgress?.completion_stats?.pass_rate || 0}%
                  </p>
                </div>
                <TrendingUp className="w-8 h-8 text-primary" />
              </div>
            </CardContent>
          </Card>
          <Card className="shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground fw-bold">
                    Completed
                  </p>
                  <p className="text-2xl font-bold text-green-600">
                    {assessmentProgress?.completion_stats?.passed_assessments ||
                      0}
                  </p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          <Card className="shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground fw-bold">
                    In Progress
                  </p>
                  <p className="text-2xl font-bold text-blue-600">
                    {assessmentProgress?.completion_stats?.total_assessments -
                      assessmentProgress?.completion_stats
                        ?.passed_assessments || 0}
                  </p>
                </div>
                <Clock className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        <div>
          {/* Main Content */}
          <div className="space-y-8">
            {/* Learning Milestones */}
            <div className="flex items-center space-x-2 mt- mb-1 text-black mb-8">
              <Flag className="w-5 h-5" />
              <h4 className="pt-2 ml-1">Learning Milestones</h4>
            </div>

            <div className="space-y-6">
              {detailRoadmap &&
                detailRoadmap.highLevelRoadmap.map(
                  (milestone: any, index: number) => (
                    <div
                      key={index}
                      className={`border-l-4 ${getPriorityColor(
                        milestone.phase
                      )} bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow`}
                    >
                      <div className="space-y-4">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-3">
                            <div className="flex-1">
                              <h3 className="font-semibold text-lg text-foreground mb-0">
                                <div className="flex items-center space-x-3">
                                  <div className="p-2 rounded-lg text-blue-600 bg-blue-100">
                                    <Star className="w-5 h-5" />
                                  </div>
                                  <div>
                                    {milestone.phase} (
                                    {detailRoadmap.careerTitle})
                                  </div>
                                </div>
                              </h3>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center justify-between text-sm text-muted-foreground font-bold">
                          <div className="flex items-center space-x-1">
                            <Clock className="w-4 h-4" />
                            <span>{milestone.duration}</span>
                          </div>
                        </div>

                        <div className="space-y-2 bg-light p-4 rounded-4">
                          {Object.keys(milestone.resources).map((title) => {
                            const url = milestone.resources[title]; // inferred as string
                            return (
                              <div key={title}>
                                <div className="font-semibold">{title}:</div>
                                <a
                                  href={url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-primary text-decoration-underline text-wrap d-block"
                                  style={{ wordBreak: "break-all" }}
                                >
                                  {url}
                                </a>
                              </div>
                            );
                          })}
                        </div>

                        <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                          <Info className="w-4 h-4" />
                          <div>
                            Some of the suggested links might not be live at the
                            moment. If a link doesn’t open, you can explore the
                            same topic on other trusted learning platforms.
                          </div>
                        </div>

                        <div className="grid md:grid-cols-2 gap-4">
                          {milestone.topics.map((t: any, index: number) => (
                            <>
                              <div
                                key={index}
                                className="flex items-start space-x-4 "
                              >
                                <div className="pt-2 flex-1">
                                  {/* <p className="text-muted-foreground"> */}
                                  <div className="d-flex flex-column flex-sm-row align-items-start justify-content-between gap-2 mb-2">
                                    <div>
                                      <div className="flex items-start space-x-2 mb-2">
                                        <div className="w-6 h-6 bg-primary/20 rounded-full flex items-center justify-center">
                                          <span className="font-semibold text-primary">
                                            {index + 1}
                                          </span>
                                        </div>
                                        <div className="font-medium">
                                          {t.topic}:
                                        </div>
                                      </div>
                                    </div>
                                    <div>
                                      {t.score >= 60 ? (
                                        <div className="flex items-center text-green-600 text-sm font-medium">
                                          <CheckCircle2 className="w-4 h-4 mr-1" />
                                          Completed ({t.score || 0}%)
                                        </div>
                                      ) : (
                                        <div>
                                          <Button
                                            size="sm"
                                            onClick={() =>
                                              handleOpenAssessment(t)
                                            }
                                            className="bg-accent hover:bg-accent/90 text-white"
                                          >
                                            <FileText className="w-4 h-4 mr-1" />
                                            Assessment
                                          </Button>
                                          <div className="flex justify-center mt-2 items-center text-muted text-sm font-medium">
                                            <BadgeInfo className="w-4 h-4 mr-1" />
                                            Pending ({t.score || 0}%)
                                          </div>
                                        </div>
                                      )}
                                    </div>
                                  </div>

                                  {t.subtopics?.map((s: any) => (
                                    <div key={s} className="text-sm mb-1 ms-8">
                                      - {s}
                                    </div>
                                  ))}
                                  {/* </p> */}
                                </div>
                              </div>
                            </>
                          ))}
                        </div>

                        <hr />

                        <div>
                          <h6>Outcomes:</h6>
                          <div className="flex flex-wrap gap-2">
                            {milestone.outcomes.map(
                              (outcomes: string, index: number) => (
                                <Badge
                                  key={index}
                                  className="text-gray-600 bg-gray-100"
                                >
                                  {outcomes}
                                </Badge>
                              )
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                )}
            </div>

            <div className="flex items-center space-x-2 mt-6 mb-1 text-black">
              <Flag className="w-5 h-5" />
              <h4 className="pt-2 ml-1">Capstone Projects</h4>
            </div>
            <Card className="shadow-sm">
              <CardContent className="pt-8">
                <div className="flex items-center justify-between">
                  <div>
                    {detailRoadmap &&
                      detailRoadmap.capstoneProjects.map(
                        (project: any, index: number) => (
                          <div key={index} className="space-y-2 mb-4">
                            <div className="flex items-center space-x-3">
                              <div className="p-2 rounded-lg text-blue-600 bg-blue-100">
                                <BarChart3 className="w-5 h-5" />
                              </div>
                              <h5>{project.title}</h5>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Clock className="w-4 h-4" />
                              <span>{project.duration}</span>
                            </div>
                            <div className="font-semibold text-muted mt-2">
                              {project.description}
                            </div>

                            {index <
                              detailRoadmap.capstoneProjects.length - 1 && (
                              <hr />
                            )}
                          </div>
                        )
                      )}
                  </div>
                  <div></div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Assessment Modal */}
      <Dialog open={showAssessmentModal} onOpenChange={setShowAssessmentModal}>
        <DialogContent
          className="overflow-y-auto"
          style={{ width: 800, maxWidth: "100%", maxHeight: "80%" }}
        >
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <FileText className="w-5 h-5 text-primary" />
              <span>Assessment</span>
            </DialogTitle>
            <DialogDescription>
              Answer the following questions to complete your assessment. You
              need 60% or higher to pass.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {selectedMilestone &&
              generatedQuestions?.questions?.map(
                (question: any, index: number) => (
                  <div key={question.id} className="space-y-3">
                    <Label className="text-base font-semibold">
                      Question {index + 1}: {question.question}
                    </Label>

                    {question.options ? (
                      <RadioGroup
                        value={
                          assessmentAnswers.find(
                            (a: any) => a.id === question.id
                          )?.user_answer || ""
                        }
                        onValueChange={(value: any) =>
                          handleAssessmentAnswerChange(question.id, value)
                        }
                      >
                        {Object.values(question.options || {}).map(
                          (option, optionIndex) => (
                            <div
                              key={optionIndex}
                              className="flex items-center space-x-2"
                            >
                              <RadioGroupItem
                                value={option} // ✅ use option text as value
                                id={`${question.id}-${optionIndex}`}
                              />
                              <Label
                                htmlFor={`${question.id}-${optionIndex}`}
                                className="font-normal cursor-pointer ms-2"
                              >
                                {option}
                              </Label>
                            </div>
                          )
                        )}
                      </RadioGroup>
                    ) : (
                      <Textarea
                        placeholder="Type your answer here..."
                        value={
                          assessmentAnswers.find(
                            (a: any) => a.id === question.id
                          )?.user_answer || ""
                        }
                        onChange={(e) =>
                          handleAssessmentAnswerChange(
                            question.id,
                            e.target.value
                          )
                        }
                        rows={4}
                        className="w-full"
                      />
                    )}
                  </div>
                )
              )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={handleCloseAssessmentModal}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmitAssessment}
              className="bg-primary hover:bg-primary/90"
              disabled={generatedQuestions?.questions?.some(
                (q: any) =>
                  !assessmentAnswers.find((a: any) => a.id === q.id)
                    ?.user_answer ||
                  assessmentAnswers.find((a: any) => a.id === q.id)
                    ?.user_answer === ""
              )}
            >
              Submit Assessment
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Result Modal */}
      <Dialog open={showResultModal} onOpenChange={setShowResultModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              {passed ? (
                <CheckCircle className="w-6 h-6 text-green-600" />
              ) : (
                <XCircle className="w-6 h-6 text-red-600" />
              )}
              <span>{passed ? "Congratulations!" : "Assessment Failed"}</span>
            </DialogTitle>
          </DialogHeader>

          <div className="py-6 space-y-4">
            <div className="text-center">
              <p className="text-4xl font-bold mb-2">
                {assessmentResult?.Correct_Answers} /{" "}
                {assessmentResult?.Total_Questions}
              </p>
              <p className="text-muted-foreground">
                Score: {assessmentResult?.Overall}
              </p>
            </div>

            {passed ? (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-green-800">
                  <CheckCircle className="w-5 h-5 inline mr-2" />
                  You have successfully completed the assessment!
                </p>
              </div>
            ) : (
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 space-y-3">
                <p className="text-orange-800">
                  <AlertCircle className="w-5 h-5 inline mr-2" />
                  Summary
                </p>
                <p className="text-sm text-orange-700">
                  {assessmentResult?.Summary?.map(
                    (point: any, index: number) => (
                      <div key={index} className="mb-1">
                        {point}
                      </div>
                    )
                  )}
                </p>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button
              onClick={handleCloseResultModal}
              className="bg-primary hover:bg-primary/90 w-full"
            >
              Continue Learning
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Footer onNavigate={onNavigate} isAuthenticated={isAuthenticated} />
    </div>
  );
}
